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
