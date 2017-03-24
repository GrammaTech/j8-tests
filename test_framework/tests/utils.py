"""
The various utils for tests
"""
import os
import pytest
import subprocess
import functools

def generate_classpath(tool_name, tool_path):
    '''
        takes in tools_path generates the classpath
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
        # XXX  may be read ant file
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

def get_stdout(cmd):
    """
        function takes in cmd
        returns shell ouput
    """
    try:
        out = subprocess.check_output(cmd)
        out = out.decode("utf-8").strip('\n')
    except:
        return None
    return out

def change_dir(test_dir):
    '''
     A decorator to change to test dir
     and return to start directory
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

