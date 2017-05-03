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

def parse_edges(lines):
    '''
    Turn an iterator of strings of the form <src-node> -> <tgt-node>
    into a list of (src,tgt) pairs
    '''
    return [tuple(line.split(" -> ", 2)) for line in lines]

@pytest.fixture(scope='module')
def cg(adapter,app,tmpdir_factory):
    '''
        Builds the call graph ir
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

    # cmd for fullcg
    cmd = ['java', 
        '-Djava.io.tmpdir=' + str(tmpdir_factory.mktemp('working',numbered=True)),
        '-cp', class_path, 
        adapter_name, dep_path] + jar_names + [main]
    # generate the fullcg
    stdout, _, returncode = utils.run_cmd(cmd)

    # failure message to display
    message = 'Adapter failed to produce callgraph'
    assert  returncode == 0, message
    
    # parse the edges in the adapter ouput into a list of src/dst pairs
    edges = parse_edges(stdout.splitlines())

    # build a dictionary representing the call graph
    # nodes in the dictionary map to a set of targets
    # nodes part of the call graph but without any outgoing edges
    # will exist in the dictionary but with an empty set
    cg = dict()
    for (s,t) in edges:
        if s in cg:
            cg[s].add(t)
        else:
            cg[s] = set((t,))
        if not t in cg:
            cg[t] = set()
    return cg

def test_callgraph_edges(cg,app):
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)

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

    with open(expected, 'r') as f:
        edges = parse_edges(l.rstrip("\n") for l in f)
        
    for (s,t) in edges:
        assert s in cg, "call graph contains " + s
        assert t in cg, "call graph contains " + t
        assert t in cg[s], "call graph contains " + s + " -> " + t

def test_callgraph_nodes(cg,app):
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)

    # ground truth
    expected = os.path.join(app_path, 'groundtruth', 'callgraph_nodes')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
       # log the message
        utils.get_logger().warning(message)
        pytest.skip(message)

    with open(expected, 'r') as f:
        nodes = [l.strip() for l in f]
    
    for n in nodes:
        assert n in cg, "call graph contains " + n
