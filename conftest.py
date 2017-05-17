'''
    Parses the command line options and uses them to set the fixtures
    Ref : https://docs.pytest.org/en/latest/example/simple.html
    Sets all the static global variables
'''
import pytest
import os

def split_tool(s):
    l = s.split('=', 2)
    if len(l) < 2:
        raise ValueError("Usage: --tool name=/path/to/tool")
    return (l[0].lower(), l[1])

def pytest_addoption(parser):
    ''' Command line options '''
    parser.addoption("--tool", action="append", type=split_tool, help="tool_name=tool_path")
    parser.addoption("--conf_file", help="configuration file")
    parser.addoption("--app", action="append", type=str.lower, help="target app name")
    parser.addoption("--slow", action="store_true")

def pytest_namespace():
    '''
        Globally available dictionary
        root_dir : root i.e. the top level directory
    '''
    return {
            'root_dir' : os.getcwd(),
            }
