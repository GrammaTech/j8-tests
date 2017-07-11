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
    Performs automatic test discovery using fixtures. Creates two dynamic fixtures
    and uses them to generate a test for every tool and every application.
    Tools are identified by a pair (tool, tool_path) where tool is the tool's
    name and tool_path specifies the path where the tool has been built and
    installed.
'''

import pytest
import itertools
import json
import os
import glob
import re

def pytest_generate_tests(metafunc):
    '''
        Generate tests from combinations of fixtures
        for every tool and every app
    '''
    if 'adapter' in metafunc.fixturenames:
        # build tool_list as specified by --tool on the command line
        tool_list = metafunc.config.option.tool
        if not tool_list:
            tool_list = []
        elif not isinstance(tool_list, list):
            tool_list = [tool_list]
        
        # build tool_list as specified in the configuration file
        if metafunc.config.option.conf_file:
            try:
                with open(metafunc.config.option.conf_file, 'r') as fread:
                    tool_list = json.load(fread)
            except:
                tool_list = []

        # generate adapter fixture for every tool in tool_list
        metafunc.parametrize('adapter', tool_list,
            ids=[n for(n,_) in tool_list],
            indirect=True)

    # generate app fixture for every app
    if 'app' in metafunc.funcargnames:
        # case where app_list is passed on the command line
        app_list = metafunc.config.option.app
        # case where app_list is generated from contents of src/app/ directory
        if not app_list:
            app_list = [os.path.basename(x) for x in\
                         glob.glob(os.path.join(pytest.root_dir, 'src', 'apps', '*'))]
        elif isinstance(app_list, str):
            app_list = [app_list]
        metafunc.parametrize('app', app_list, scope='module')


def pytest_collection_modifyitems(config, items):
    if config.option.slow:
        return
    try:
        with open(os.path.join(pytest.root_dir, 'slow_tests.txt')) as f:
            slow_tests = [re.compile(l.rstrip("\n")) for l in f]
    except (OSError, re.error):
        return
        
    for item in items[:]:
        if any(i.match(item.name) for i in slow_tests):
            #item.warn('', "Skipping long running test " + item.name)
            items.remove(item)
