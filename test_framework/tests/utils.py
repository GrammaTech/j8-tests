"""
The various utils for tests
The generate classpath takes in the path and returns class path required
Change dir, the test system goes to test evaluators
and builds the adaptor for that evaluator
"""
import os
import pytest
import subprocess
import functools

def generate_classpath(tool_name, tool_path):
    '''
        takes in tools_path generates the classpath
        These are specific rules for each tool
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
     A decorator to change to test dir and return to start directory
     This is useful because we want the adapters to be build in same place
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
            #change back
            os.chdir(cur_dir)
        return wrapper
    return decorator

