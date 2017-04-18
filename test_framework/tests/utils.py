"""
Following Utilities for running test
1) Generate appropriate classpath from tool path
2) Decorator to change directory
"""
import os
import pytest
import subprocess
import functools
import logging
import sys

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

def get_logger():
    ''' common logger interface'''
    logger = logging.getLogger('JAVA8_Tests')
    return logger

def run_cmd(cmd):
    '''
        Use the subprocess to execute a shell command
        This would return stdout, stderr and return code
        User should use this interface to run as it logs the error
    '''
    # log to file when error
    logger = get_logger()
    use_logger = False
    # log only to file
    if len(logger.handlers) > 0 and\
        isinstance(logger.handlers[0], logging.FileHandler):
        use_logger = True
    try:
        proc = subprocess.Popen(cmd,\
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        # convert byte to string
        stderr = stderr.decode("utf-8")
        stdout = stdout.decode("utf-8")
        # get the return code
        returncode = proc.returncode
        if not returncode == 0 and\
            use_logger:
            logger.debug(stdout)
            logger.debug(stderr)
    # incase of error set everything null
    except:
        returncode = -1
        stdout = None
        stderr = None
        if use_logger:
            logger.debug(sys.exc_info())
    return stdout, stderr, returncode
