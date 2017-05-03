'''
Call graph test family:

The call graph family currently tests for the presense of edges in the call 
graph. Each adapter is expected to output all edges in the call graph, and the
evaluator performs various checks on it. For details on the format see:
https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir

The ground truth for the call graph test is usually manually generated
(but often the full call graph output is useful to copy and paste from).
Edges should be added which reflect tricky constructs like lambdas and
default methods.
'''
import pytest
import subprocess
import os
import sys
import filecmp
import glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

def test_callgraph(adapter,app,tmpdir_factory):
    xtest_callgraph(adapter,app,tmpdir_factory)

@utils.change_dir(os.path.dirname(__file__))
def xtest_callgraph(adapter,app,tmpdir_factory):
    '''
        Does the callgraph test
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
    expected = os.path.join(app_path, 'groundtruth', 'callgraph_edges')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
       # log the message
        utils.get_logger().warning(message)
        pytest.skip(message)

    # cmd for fullcg
    cmd = ['java', 
        '-Djava.io.tmpdir=' + str(tmpdir_factory.getbasetemp()),
        '-cp', class_path, 
        adapter_name, dep_path] + jar_names + [main]
    # generate the fullcg
    stdout, _, returncode = utils.run_cmd(cmd)

    # failure message to display
    message = 'Adapter failed to produce callgraph'
    assert  returncode == 0, message
    
    with open(expected, 'r') as f:
        expected_list = set(l.strip() for l in f)
    fullcg_list = set(stdout.splitlines())

    # get the intersection of expected and fullcg
    actual = expected_list.intersection(fullcg_list)
    message = 'Ground Truth differs for app %s' % app
    # actual and expected sets should be the same
    assert actual == expected_list, message
