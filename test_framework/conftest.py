'''
    Parses the command line options and uses them to set the fixtures
    Ref : https://docs.pytest.org/en/latest/example/simple.html
    Set all the static global variables
'''
import pytest
import os

def pytest_addoption(parser):
    ''' cmd line options '''
    parser.addoption("--tool", action="append", help="name of the tool")
    parser.addoption("--tool_path", action="append",\
            help="pass the path to tool")
    parser.addoption("--conf_file", help="configuration file")
    parser.addoption("--log_output", \
            help="Set it to direct log output to a logfile")
    parser.addoption("--app", action="append")

@pytest.fixture
def tool(request):
    ''' user provided tool name '''
    return request.config.getoption("--tool")

@pytest.fixture
def tool_path(request):
    ''' user provided tool path '''
    return request.config.getoption("--tool_path")

def pytest_namespace():
    '''
        return dict of the following variables to be made globally available,
        root_dir : root or the top level directory
    '''
    return {
            'root_dir' : os.getcwd(),
            }
