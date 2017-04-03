"""
    Main driver program for test framework.
    This checks system prerequisites and then calls the pytest
    Any command line arguments are passed to pytest
    Usage : python setup.py --tool --tool_path
"""

import sys
import os
import subprocess

def run_check():
    '''
        run various checks
        1) operating system is Linux
        2) Java 8 is installed
        3) python version 2.7 or greater is installed
        4) pytest is installed
    '''
    # work on Linux only
    if not sys.platform.startswith('linux'):
        sys.exit('Error : Test suite only compatible with\
                Linux operating system')

    # check if python 2.7 and greater
    status =  sys.version_info >= (2,7)
    if not status:
        sys.exit('Error : python version atleast 2.7 not found')
    print('python version found %s ' % sys.version_info)

    # check for Java && Java 8
    try:
        proc = subprocess.Popen(['java', '-version'],\
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        # check for Java 8
        try:
            version = stderr.split('\n')[0].split(" ")[2]
            print('Java version found %s' % version)
            if not '1.8' in version:
                sys.exit('Error : Java 8 not found')
        except:
            print(sys.exc_info())
            sys.exit('Error : Java 8 not found')

    except:
        print(sys.exc_info())
        sys.exit('Error : Java not found')

    # check pytest
    try:
        subprocess.check_call('pytest --version', shell=True)
    except subprocess.CalledProcessError, subprocess.OSError:
        sys.exit('Error : pytest not found')

if __name__ == "__main__":
    # system requirement
    run_check()
    # call pytest
    cmd = 'pytest ' + ' '.join(sys.argv[1:])
    subprocess.call(cmd, shell=True)
