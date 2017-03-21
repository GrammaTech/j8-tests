'''
This globs the tools and apps
create a global function which can be used in every subdir
'''
import pytest
import glob
import os
import itertools

@pytest.fixture(scope='session')
def tools():
    '''
        get all the tools directory
    '''
    tools_list = glob.glob('src/tools/*')
    return tools_list

@pytest.fixture(scope='session')
def apps():
    '''
        get all the apps dir
    '''
    apps_list = glob.glob('src/apps/*')
    return apps_list

def combinations():
    '''
        cross product of tools and apps
    '''
    tools_list = [os.path.basename(x) for x in glob.glob('src/tools/*')]
    apps_list = [os.path.basename(x) for x in glob.glob('src/apps/*')]
    return [tup for tup in itertools.product(tools_list, apps_list)]

def pytest_namespace():
    '''
        pytest global variable
    '''
    return {'tool_app': combinations()}


