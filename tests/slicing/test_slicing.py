'''
    pytest file
    slicing test
'''
import pytest # pytest root dir
import subprocess # forking a child process
import os
import sys # path append
import filecmp # file comparison
import glob #glob.glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

def test_slicing(adapter,app):
    xtest_slicing(adapter,app)

@utils.change_dir(os.path.dirname(__file__))
def xtest_slicing(adapter,app):
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

    query = open(os.path.join(app_path, 'groundtruth', 'slicing_query'), 'r')
    if not query:
        message = "slicing query for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
        # log the message
        utils.get_logger().warning(message)
        pytest.skip(message)

    # cmd for fullcg
    cmd = ['java', '-cp', class_path, adapter_name, dep_path] + jar_names + [main]
    # generate the fullcg
    stdout, _, returncode = utils.run_cmd(cmd,stdin=query)
    query.close()
    
    # failure message to display
    message = 'Adapter failed to produce results'
    assert  returncode == 0, message

    message = ""
    expected_f = open(os.path.join(app_path, 'groundtruth', 'slicing_result'), 'r')
    for (expected,actual) in zip(expected_f, stdout.split("\n")):
        expected = expected.rstrip('\n')
        if expected != actual:
            message += expected + " != " + actual + "\n"
    if message:
        assert False, message
