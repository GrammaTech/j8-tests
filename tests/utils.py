# This material is based upon work supported by the United States Air Force
# and DARPA under Contract No. FA8750-15-C-0082. Any opinions, findings and
# conclusions or recommendations expressed in this material are those of
# the author(s) and do not necessarily reflect the views of the United
# States Air Force and DARPA.
#
#
# Copyright 2017 GrammaTech, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# If you are interested in making contributions, then please contact
# info@grammatech.com
"""
Utilities for running tests:
1) Generate classpath for tool
2) run_cmd wrapper for subprocess
"""
import os
import subprocess

def generate_classpath(tool_name, tool_path):
    '''
        Return the appropriate Java classpath for building adapters
        @tool : tool name, case sensitive
        @tool_path : directory where tool has been built/installed
    '''
    if tool_name == 'wala':
        # list of WALA packages
        prj = ['core.tests', 'core', 'shrike', 'util']
        # join the packages with tool_path
        return [os.path.join(tool_path,\
                'com.ibm.wala.' +  pt, 'target/classes')\
                for pt in prj]

    elif tool_name == 'soot':
        # class path for dependencies
        # root_dir is set in top level conftest
        dep = [tool_path + '/../heros/heros-trunk.jar',
               tool_path + '/../jasmin/libs/*']
        # soot path is set from tool_path
        cp_soot = [os.path.join(tool_path, 'classes'),
                   os.path.join(tool_path, 'libs/*')]
        # combined classpath
        return dep + cp_soot

    elif tool_name == 'accrue':
        # set classpath
        return [
            os.path.join(tool_path, 'target/classes'),
            os.path.join(tool_path, 'target/dependency/*'),
            os.path.join(tool_path, 'data')
            ]
            
    elif tool_name == 'joana':
        return [os.path.join(tool_path, 'dist', 'joana.wala.jodroid', 'classes')]

    else:
        raise KeyError(tool_name + " not supported")

def run_cmd(cmd,**kwargs):
    '''
        Use subprocess module to execute a shell command
        This will stdout and theow if the command fails
    '''
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,**kwargs)
    stdout = proc.stdout.read()
    proc.stdout.close()
    proc.wait()
    assert proc.returncode == 0, ' '.join(cmd) + " failed"
    return stdout
