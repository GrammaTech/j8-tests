"""
Utilities for running tests:
1) Generate classpath for tool
2) run_cmd wrapper for subprocess
"""
import os
import subprocess

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

def run_cmd(cmd,**kwargs):
    '''
        Use subprocess module to execute a shell command
        This will stdout and theow if the command fails
    '''
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,**kwargs)
    stdout = proc.stdout.read()
    proc.stdout.close()
    proc.wait()
    assert proc.returncode == 0, ' '.join(cmd) + " failed"
    return stdout
