"""
    Main driver program for test framework.
    This checks system prerequisites and then calls the pytest
    Any command line arguments are passed to pytest
    Usage : python setup.py --tool --tool_path
"""

import sys
import os
import subprocess # call, Popen
import logging # logging
import time # strftime
import pytest

def run_check(logger):
    '''
        run various checks
        1) operating system is Linux
        2) Java 8 is installed
        3) python version 2.7 or greater is installed
    '''
    # work on Linux only
    if not sys.platform.startswith('linux'):
        sys.exit('Error : Test suite only compatible with\
                Linux operating system')

    # check if python 2.7 and greater
    status = sys.version_info >= (2, 7)
    version = str(sys.version_info.major) + '.' + str(sys.version_info.minor)
    if not status:
        sys.exit('Error : python version atleast 2.7 not found')
    logger.info('python version found %s ' % version)

    # check for Java && Java 8
    try:
        proc = subprocess.Popen(['java', '-version'],\
                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        # byte to str
        stderr = stderr.decode("utf-8")
        stdout = stdout.decode("utf-8")
        # check for Java 8
        try:
            version = stderr.split('\n')[0].split(" ")[2]
            logger.info('Java version found %s' % version)
            if not '1.8' in version:
                sys.exit('Error : Java 8 not found')
        except:
            logger.error(sys.exc_info())
            sys.exit('Error : Java 8 not found')

    except:
        logger.error(sys.exc_info())
        sys.exit('Error : Java not found')


if __name__ == "__main__":
    # set logging
    logger = logging.getLogger('JAVA8_Tests')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # if log_output is passed to cmd line write the log to file
    if '--log_output' in sys.argv:
        log_dir = 'log_run'
        # create a log directory
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        # use timestamp as the name of the log file
        timestr = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, timestr + '.log')
        # create file handler
        file_handler = logging.FileHandler(log_file)
        # set the format
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else: # use console writer
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
    # system requirement
    logger.info('Running System Check')
    run_check(logger)
    # call pytest, use '.' to run in current directory
    pytest_param = ' '.join(sys.argv[1:]) + ' .'
    pytest.main(pytest_param)
