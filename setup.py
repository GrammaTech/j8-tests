"""
    Main driver program for test framework.
    This checks system prerequisites and then calls pytest
    Any command line arguments are passed to pytest
    Usage : python setup.py --tool wala=/path/to/wala
"""

import sys
import os
import subprocess
import logging
import time
import pytest

if __name__ == "__main__":
    # configure logging
    logger = logging.getLogger('JAVA8_Tests')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # use file_hander for logging if --log_output flag is set
    if '--log_output' in sys.argv:
        sys.argv.remove('--log_output')
        log_dir = 'log_run'
        # create a logging directory
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

    # call pytest in current directory using '.'
    sys.argv.extend('.');
    sys.exit(pytest.main(sys.argv[1:]))
