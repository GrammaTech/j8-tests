'''
    Parses the command line options and uses them to set the fixtures
    Ref : https://docs.pytest.org/en/latest/example/simple.html
    Sets all the static global variables
'''
import pytest
import os

def pytest_addoption(parser):
    ''' Command line options '''
    parser.addoption("--tool", action="append", help="tool name")
    parser.addoption("--tool_path", action="append",\
            help="tool location")
    parser.addoption("--conf_file", help="configuration file")
    parser.addoption("--app", action="append", help="target app name")

def pytest_namespace():
    '''
        Globally available dictionary
        root_dir : root i.e. the top level directory
    '''
    return {
            'root_dir' : os.getcwd(),
            }
