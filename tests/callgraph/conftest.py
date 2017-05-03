'''
    Adapter fixture for the callgraph tests
    See https://github.com/GrammaTech/j8-tests/blob/master/Readme.md#callgraph-ir
'''
import pytest # pytest root dir
import subprocess # forking a child process
import os
import sys # path append
import filecmp # file comparison
import glob #glob.glob

sys.path.append(os.path.join(pytest.root_dir, 'tests'))
import utils

@pytest.fixture(scope="session", autouse=True)
def adapter(request):
    return xadapter(*request.param)

@utils.change_dir(os.path.dirname(__file__))
def xadapter(tool_name, tool_path):
    '''
        build the call graph adapter (<tool>CGAdapter) from tool_name (the
        name of the too, e.g. wala) and the path to the tool's distribution

    '''
    adapter_name = tool_name.title() + 'CGAdapter';
    # set class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    class_path.insert(0, os.curdir)
    class_path = os.pathsep.join(class_path)
    # compile adapter
    cmd = ['javac', '-cp', class_path, adapter_name + '.java']
    # run the adapter cmd
    _, _, returncode = utils.run_cmd(cmd)
    # check if the build passed
    assert returncode == 0
    return (class_path, adapter_name)
