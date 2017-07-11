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
    Parses the command line options and uses them to set the fixtures
    Ref : https://docs.pytest.org/en/latest/example/simple.html
    Sets all the static global variables
'''
import pytest
import os

def split_tool(s):
    l = s.split('=', 2)
    if len(l) < 2:
        raise ValueError("Usage: --tool name=/path/to/tool")
    return (l[0].lower(), l[1])

def pytest_addoption(parser):
    ''' Command line options '''
    parser.addoption("--tool", action="append", type=split_tool, help="tool_name=tool_path")
    parser.addoption("--conf_file", help="configuration file")
    parser.addoption("--app", action="append", type=str.lower, help="target app name")
    parser.addoption("--slow", action="store_true")

def pytest_namespace():
    '''
        Globally available dictionary
        root_dir : root i.e. the top level directory
    '''
    return {
            'root_dir' : os.getcwd(),
            }
