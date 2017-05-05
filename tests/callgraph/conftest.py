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
def adapter(request, tmpdir_factory):
    '''
        build the call graph adapter (<tool>CGAdapter) from tool_name (the
        name of the too, e.g. wala) and the path to the tool's distribution

    '''
    (tool_name, tool_path) = request.param
    adapter_name = tool_name.title() + 'CGAdapter';
    objdir = str(tmpdir_factory.mktemp('classes', numbered=True))
    # set class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    # compile adapter
    cmd = ['javac', 
        '-d', objdir,
        '-cp', os.pathsep.join(class_path), 
        os.path.join(os.path.dirname(__file__), adapter_name + '.java')
        ]
    utils.run_cmd(cmd)

    # insert our temporary directory into the classpath (before the
    # tool's)
    class_path.insert(0, objdir)
    return (os.pathsep.join(class_path), adapter_name)
