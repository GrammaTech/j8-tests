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

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

@utils.change_dir(os.path.dirname(__file__))
def test_adapters(tool_list):
    '''
        builds the adapter
        It takes the tool_path, gets the class path
        The change_dir ensures the adapter is build
        in the same directory

    '''
    tool_name, tool_path = tool_list
    print(tool_list)
    # set class path
    classpath = utils.generate_classpath(tool_name, tool_path)
    # build adaptor
    cmd = ' '.join(['javac', '-cp', classpath, tool_name + 'CG.java'])
    print(cmd)
    value = subprocess.call(cmd, shell=True)
    # check if the build passed
    assert value == 0


@utils.change_dir(os.path.dirname(__file__))
def test_callgraph(comb):
    '''
        Does the callgraph test
    '''
    tool, app = comb
    tool_name, tool_path = tool
    # set app path src/apps
    app_path = os.path.join(pytest.root_dir, 'src/apps', app)
    # get class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    # adapter
    adapter = tool_name + 'CG'
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
        pytest.skip(message)

    # get full cg
    cmd = ' '.join(['java', '-cp', class_path, adapter,
        os.path.join(app_path, '*.jar'), main, '> fullcg'])
    subprocess.call(cmd, shell=True)

    # actual value
    cmd = ' '.join(['export LANG=C && ',
        'grep', '-Ff', expected, 'fullcg | sort | uniq > actual'])
    subprocess.call(cmd, shell=True)

    # check the difference
    status = filecmp.cmp(expected, 'actual', shallow=False)
    # check if passed
    assert status == True
