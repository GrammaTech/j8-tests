'''
Parses the command line options and makes it available for test apdapters
Set all the static global variables here
'''
import pytest
import glob
import os

def pytest_addoption(parser):
    ''' user defined values '''
    parser.addoption("--tool", action="append", help="pass the tools name")
    parser.addoption("--tool_path", action="append",\
            help="pass the path to tool")
    parser.addoption("--conf_file", help="run using config")

@pytest.fixture
def tool(request):
    ''' user defined tool '''
    return request.config.getoption("--tool")

@pytest.fixture
def tool_path(request):
    ''' user defined tool path, convert to class path'''
    return request.config.getoption("--tool_path")

def pytest_namespace():
    '''
        pytest global variable used in every module
        root_dir for the test
        app_list : glob of all the applications
    '''
    return {
            'apps_list': [os.path.basename(x) for x in\
                glob.glob('src/apps/*')],
            'root_dir' : os.getcwd(),
            }
