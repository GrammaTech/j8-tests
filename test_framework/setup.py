"""
Pytest tests
"""

import sys
import os
import subprocess

def run_check():
    ''' run various checks
        1) os == linux
        2) java && java8
        3) python
        4) pytest
    '''
    # work on linux only
    if not sys.platform.startswith('linux'):
        sys.exit('Error : Not on a compatible Operation System')
    #check for java8
    ret_code = subprocess.call('java -version', shell=True)
    if not ret_code == 0:
        sys.exit('java not found')
    #check if python3
    ret_code = subprocess.call('python --version', shell=True)
    if not ret_code == 0:
        sys.exit('python not found')
    #check if pytest
    ret_code = subprocess.call('pytest --version', shell=True)
    if not ret_code == 0:
        sys.exit('pytest not found')

if __name__ == "__main__":
    # system requirement
    run_check()
    # set env
    subprocess.call('export HOME2='+ os.getcwd(), shell=True)
    # call pytest
    subprocess.call('pytest', shell=True)
