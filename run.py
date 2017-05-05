"""
    Main driver program for test framework.
    Any command line arguments are passed to pytest
    Usage : python run.py --tool wala=/path/to/wala
"""

import sys
import pytest

sys.exit(pytest.main(sys.argv[1:]))
