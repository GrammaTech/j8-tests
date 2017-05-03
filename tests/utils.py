"""
Utilities for running tests:
1) Generate classpath for tool
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
        Return the appropriate Java classpath for building adapters
        @tool : tool name, case sensitive
        @tool_path : directory where tool has been built/installed
    '''
    if tool_name == 'wala':
        # list of WALA packages
        prj = ['core.tests', 'core', 'shrike', 'util']
        # join the packages with tool_path
        return [os.path.join(tool_path,\
                'com.ibm.wala.' +  pt, 'target/classes')\
                for pt in prj]

    elif tool_name == 'soot':
        # class path for dependencies
        # root_dir is set in top level conftest
        dep = [tool_path + '/../heros/heros-trunk.jar',
               tool_path + '/../jasmin/libs/*']
        # soot path is set from tool_path
        cp_soot = [os.path.join(tool_path, 'classes'),
                   os.path.join(tool_path, 'libs/*')]
        # combined classpath
        return dep + cp_soot

    elif tool_name == 'accrue':
        # set classpath
        return [
            os.path.join(tool_path, 'target/classes'),
            os.path.join(tool_path, 'target/dependency/*'),
            os.path.join(tool_path, 'data')
            ]
            
    elif tool_name == 'joana':
        return [os.path.join(tool_path, 'dist', 'joana.wala.jodroid', 'classes')]

    else:
        raise KeyError(tool_name + " not supported")

def change_dir(target_dir):
    '''
    This decorator does the following:
    1) Change to target directory
    2) Execute the callee function
    3) Change back to last working directory
    @target_dir : target directory
    '''
    def decorator(func):
        ''' main decorator'''
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ''' inner wrapper '''
            current_dir = os.getcwd()
            os.chdir(target_dir)
            r = func(*args, **kwargs)
            os.chdir(current_dir)
            return r
        return wrapper
    return decorator

def get_logger():
    ''' common logger interface'''
    logger = logging.getLogger('JAVA8_Tests')
    return logger

def run_cmd(cmd,stdin=None):
    '''
        Use subprocess module to execute a shell command
        This will return stdout, stderr and shell return code
        This interface supports logging
    '''
    # log errors
    logger = get_logger()
    # default logging handler is console, skip logging
    use_logger = False
    #  check if logging handler is file, use logging
    if len(logger.handlers) > 0 and\
        isinstance(logger.handlers[0], logging.FileHandler):
        use_logger = True
    try:
        proc = subprocess.Popen(cmd,\
                stdin=stdin,\
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
    # in case of error set everything to None
    except:
        returncode = -1
        stdout = None
        stderr = None
        if use_logger:
            logger.error(sys.exc_info())
    return stdout, stderr, returncode
