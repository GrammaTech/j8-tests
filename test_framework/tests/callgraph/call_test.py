'''
    pytest file
    1) test for adapters :
    2) test for the call graph
'''
import pytest # pytest root dir
import subprocess # forking a child process
import os
import sys # path append
import filecmp # file comparison
import glob #glob.glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

def test_adapters(tool_list):
    xtest_adapters(tool_list)

@utils.change_dir(os.path.dirname(__file__))
def xtest_adapters(tool_list):
    '''
        builds the adapter
        It takes the tool_path, gets the class path
        The change_dir ensures the adapter is build
        in the same directory

    '''
    tool_name, tool_path = tool_list
    # set class path
    classpath = utils.generate_classpath(tool_name, tool_path)
    # build adaptor
    cmd = ['javac', '-cp', classpath, tool_name + 'CGAdapter.java']
    # run the adapter cmd
    _, _, returncode = utils.run_cmd(cmd)
    # check if the build passed
    assert returncode == 0


def test_callgraph(comb):
    xtest_callgraph(comb)

@utils.change_dir(os.path.dirname(__file__))
def xtest_callgraph(comb):
    '''
        Does the callgraph test
    '''
    # setup for the test
    tool, app = comb
    tool_name, tool_path = tool

    # get class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    assert not class_path == None
    # adapter
    adapter = tool_name + 'CGAdapter'

    # set app path src/apps
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)
    dep_path = os.path.join(pytest.root_dir, 'src', 'dependencies')

    # find the app jar name
    try:
        jar_name = glob.glob(os.path.join(app_path, '*.jar'))[0]
    except:
        jar_name = os.path.join(app_path, '*.jar')

    # get main name from first line
    try:
        with open(os.path.join(app_path, 'main'), 'r') as fread:
            main = fread.readline().strip('\n')
    except:
        main = None
    assert not main == None, main

    # ground truth
    expected = os.path.join(app_path, 'callgraph_expected')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
       # log the message
        utils.get_logger().warning(message)
        pytest.skip(message)

    # cmd for fullcg
    cmd = ['java', '-cp', class_path, adapter, dep_path, jar_name, main]
    # generate the fullcg
    stdout, _, returncode = utils.run_cmd(cmd)

    # failure message to display
    message = 'Adapter failed to produce callgraph'
    assert  returncode == 0, message
    # write out the fullcg
    with open('fullcg', 'w') as fwrite:
        fwrite.write(stdout)

    # get actual value
    expected_list = set()
    fullcg_list = set()
    # read fullcg from file
    with open('fullcg', 'r') as fread:
        for line in fread:
            fullcg_list.add(line)
    # read expected from file
    with open(expected, 'r') as fread:
        for line in fread:
            expected_list.add(line)
    # get the intersection of expected and fullcg
    actual = set(sorted(expected_list.intersection(fullcg_list)))
    message = 'Ground Truth differs for app %s' % app
    # actual and expected sets should be of same size
    assert len(actual) == len(expected_list) , message
    # assert the difference of actual and expected to be zero
    assert len(actual ^  expected_list) == 0, message
