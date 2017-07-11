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

# The cg fixture generates the callgraph ir for an application/tool pair
# It is represented by a dictionary mapping nodes to a set of targets
# (a node is in the set if there is an edge between the two nodes)
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
    stdout = utils.run_cmd(cmd)

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

# This test checks for edges in the call graph (from callgraph_edges)
def test_callgraph_edges(cg,app):
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)

    # ground truth
    expected = os.path.join(app_path, 'groundtruth', 'callgraph_edges')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
        pytest.skip(message)

    with open(expected, 'r') as f:
        edges = parse_edges(l.rstrip("\n") for l in f)
        
    for (s,t) in edges:
        assert s in cg, "call graph contains " + s
        assert t in cg, "call graph contains " + t
        assert t in cg[s], "call graph contains " + s + " -> " + t

# This test checks for nodes in the call graph (anywhere, it doesn't care
# how they're reachable) (from callgraph_nodes)
def test_callgraph_nodes(cg,app):
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)

    # ground truth
    expected = os.path.join(app_path, 'groundtruth', 'callgraph_nodes')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
        pytest.skip(message)

    with open(expected, 'r') as f:
        nodes = [l.strip() for l in f]
    
    for n in nodes:
        assert n in cg, "call graph contains " + n

# Quick and dirty check for a path between two nodes in the
# call graph dictionary (NB: this must not be recursive)
def has_path(g, src, tgt):
    if not src in g:
        return False
    wl = [src]
    visited = set()
    while wl:
        n = wl.pop()
        for t in g[n]:
            if t == tgt:
                return True
            if t not in visited:
                visited.add(t)
                wl.append(t)
    return False

# This test checks for paths in the call graph, a start and end
# node are given (from callgraph_paths) any we check if there is
# any path between them
def test_callgraph_paths(cg,app):
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)

    # ground truth
    expected = os.path.join(app_path, 'groundtruth', 'callgraph_paths')

    # skip  the test if the ground truth doesn't exists
    # using imperative skip option
    if not os.path.exists(expected):
        message = "Ground Truth for app %s for test %s missing"\
            % (app, os.path.basename(__file__))
        pytest.skip(message)

    with open(expected, 'r') as f:
        pairs = parse_edges(l.rstrip("\n") for l in f)

    for (s,t) in pairs:
        assert s in cg, "call graph contains " + s
        assert t in cg, "call graph contains " + t
        assert has_path(cg, s, t), "call graph has path " + s + " ... " + t
