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



@pytest.fixture(scope="session", autouse=True)
def adapter(request):
    return xadapter(*request.param)

@utils.change_dir(os.path.dirname(__file__))
def xadapter(tool_name, tool_path):
    '''
        builds the adapter
        It takes the tool_path, gets the class path
        The change_dir ensures the adapter is build
        in the same directory

    '''
    adapter_name = tool_name.title() + 'SLAdapter';
    # set class path
    class_path = utils.generate_classpath(tool_name, tool_path)
    # build adaptor
    cmd = ['javac', '-cp', class_path, adapter_name + '.java']
    # run the adapter cmd
    _, _, returncode = utils.run_cmd(cmd)
    # check if the build passed
    assert returncode == 0
    return (class_path, adapter_name)
    #os.remove(glob.glob(adapter_name + "*.class"))

