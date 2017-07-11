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
Slicing test family:

The slicing family tests currently checks for data flow between two formals.
Each "query" (a source and target formal) can have an expected result of
either data flow existing or not existing. For details on the format see:
https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#slicing-ir

The ground truth for the slicing test is manually generated. Interesting
data flow (ideally things which to though tricky constructs like lambdas and
default methods should be identified in the source code and a corresponding
pair of formals surrounding it added as a query. Both cases where data flow
is expected and not expected are interesting.
'''
import pytest
import subprocess
import os
import sys
import filecmp
import glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

def test_slicing(adapter,app,tmpdir):
    '''
        Does the slicing test
    '''
    # setup for the test
    class_path, adapter_name = adapter

    # set app path src/apps
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)
    dep_path = os.path.join(pytest.root_dir, 'src', 'dependencies')

    # find the app jar names
    jar_names = glob.glob(os.path.join(app_path, '*.jar'))

    # get main name from first line
    try:
        with open(os.path.join(app_path, 'main'), 'r') as fread:
            main = fread.readline().strip('\n')
    except:
        main = None
    assert not main == None, main

    # ground truth
    expected = os.path.join(app_path, 'groundtruth', 'slicing_expected')

    try:
        query = open(os.path.join(app_path, 'groundtruth', 'slicing_query'), 'r')
    except IOError:
        message = "slicing query for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
        # log the message
        pytest.skip(message)

    # cmd for fullcg
    cmd = ['java', 
        '-Djava.io.tmpdir=' + str(tmpdir),
        '-cp', class_path, 
        adapter_name, dep_path] + jar_names + [main]
    # generate the fullcg
    stdout = utils.run_cmd(cmd,stdin=query)
    query.close()
    
    message = ""
    expected_f = open(os.path.join(app_path, 'groundtruth', 'slicing_result'), 'r')
    for (expected,actual) in zip((l.strip() for l in expected_f), stdout.splitlines()):
        if expected != actual:
            message += expected + " != " + actual + "\n"
    if message:
        assert False, message
