# content of test_scenarios.py
import pytest
import subprocess
import os

def test_env():
    '''
      test env variable
    '''
    home2 = os.environ.get('HOME2', None)
    assert home2 is not None

def test_adaptors():
    pass

def pytest_generate_tests(metafunc):
    if 'comb' in metafunc.funcargnames:
        metafunc.parametrize('comb', pytest.tool_app)

def test_callgraph(comb):
    tool, app = comb
    cur_dir = os.getcwd()
    os.chdir('tests/callgraph')
    cmd = 'sh ./run.sh ' + tool + ' ' + app
    value = subprocess.call(cmd, shell=True)
    os.chdir(cur_dir)
    assert value == 0
