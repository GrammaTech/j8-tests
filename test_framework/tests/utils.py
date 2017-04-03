"""
Following Utilities for running test
1) Generate appropriate classpath from tool path
2) Decorator to change directory
"""
import os
import pytest
import subprocess
import functools

def generate_classpath(tool_name, tool_path):
    '''
        For a given tool_path, return the appropriate Java classpath. This
        information varies by tool and we need it to build adapters."
        @tool : tool name, match case
        @tool_path : path where tool is compiled
    '''
    if tool_name == 'Wala':
        # list of wala packages
        prj = ['core.tests', 'core', 'shrike', 'util']
        # join them with tool_path
        classpath = ".:" + ":".join([os.path.join(tool_path,\
                'com.ibm.wala.' +  pt, 'target/classes')\
                for pt in prj])
        return classpath

    if tool_name == 'Soot':
        # class path for dependencies
        # root_dir is set in top level conftest
        dep = [os.path.join(pytest.root_dir,
            'src/dependencies/heros/heros-trunk.jar'),
            os.path.join(pytest.root_dir,
            'src/dependencies/jasmin/libs/*')]
        # soot path is set from tool_path
        cp_soot = [os.path.join(tool_path, 'classes'),
                   os.path.join(tool_path, 'libs/*')]
        # combined classpath
        classpath = ".:" + ":".join(dep + cp_soot)
        return classpath


def change_dir(test_dir):
    '''
    A decorator to change to test directory, run tests and
    change to current directory
    The test adapters are compiled in same directory as the test evaluators
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # cur dir
            cur_dir = os.getcwd()
            # change to test dir
            os.chdir(test_dir)
            # the test
            func(*args, **kwargs)
            # change back
            os.chdir(cur_dir)
        return wrapper
    return decorator

