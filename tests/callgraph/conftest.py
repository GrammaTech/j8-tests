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
'''
    Adapter fixture for the callgraph tests
    See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir
'''
import pytest # pytest root dir
import subprocess # forking a child process
import os
import sys # path append
import filecmp # file comparison
import glob #glob.glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

@pytest.fixture(scope="session", autouse=True)
def adapter(request, tmpdir_factory):
    '''
        build the call graph adapter (<tool>CGAdapter) from tool_name (the
        name of the too, e.g. wala) and the path to the tool's distribution

    '''
    (tool_name, tool_path) = request.param
    adapter_name = tool_name.title() + 'CGAdapter';
    objdir = str(tmpdir_factory.mktemp('classes', numbered=True))
    # set class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    # compile adapter
    cmd = ['javac', 
        '-d', objdir,
        '-cp', os.pathsep.join(class_path), 
        os.path.join(os.path.dirname(__file__), adapter_name + '.java')
        ]
    utils.run_cmd(cmd)

    # insert our temporary directory into the classpath (before the
    # tool's)
    class_path.insert(0, objdir)
    return (os.pathsep.join(class_path), adapter_name)
