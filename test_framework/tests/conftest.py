'''
    Performs auto tests discovery using fixtures. Creates two dynamic fixtures
    and uses them to generate a test for every tool and every application.
    Tools are identified by a pair (tool, tool_path) where tool is the tool's
    name and tool_path specifies the path where the tool is found.

    The hook pytest_generate_tests helps in defining and running various
    different tests dynamically, these tests are created depending on
    different type of inputs given by user. For example, here,
    we want to run tests based on command line option for pair
    (tool, tool_path). In principle, there could be many pairs and
    we would like to run various tests for all such (tool, tool_path) pairs.
    By using the hook pytest_generate_tests gives us the option
    to create different tests dynamically.

    In order to run the test the usage for new test should be :
        new_test(tool_list)
    This will create multiple new test depending on # of (tool, tool_path)
'''

import pytest # apps_list
import itertools # product
import json #load
import logging
import os
import glob

def pytest_generate_tests(metafunc):
    '''
        generate test from combinations of fixtures
    '''
    tool_app_pair = []
    tool_list = []
    # check if the tool is passed in the cmd line opt
    # create a list of combination of tool and tool_path
    if  metafunc.config.option.tool and\
            metafunc.config.option.tool_path:
        # if only one tool is passed
        if isinstance(metafunc.config.option.tool, str):
            tool_list = [
                metafunc.config.option.tool,
                metafunc.config.option.tool_path
            ]
        # if a list of tools are passed
        elif isinstance(metafunc.config.option.tool, list):
            tool_list = zip(metafunc.config.option.tool,
                metafunc.config.option.tool_path)

    # read from a configuration file
    if metafunc.config.option.conf_file:
        try:
            with open(metafunc.config.option.conf_file, 'r') as fread:
                tool_list = json.load(fread)
        except:
            tool_list = []
            
    tool_list = [(a.title(),b) for (a,b) in tool_list]

    # create combination of tools * apps
    # for any function with parameter named 'comb'
    # create a new test with entry from combination
    if 'comb' in metafunc.funcargnames:
        apps_list = metafunc.config.option.app
        if not apps_list:
            apps_list = [os.path.basename(x) for x in\
                         glob.glob(os.path.join(pytest.root_dir, 'src', 'apps', '*'))]
        elif isinstance(apps_list, str):
            apps_list = [apps_list]
        tool_app_pair = [tup for tup in\
                itertools.product(tool_list, apps_list)]
        metafunc.parametrize('comb', tool_app_pair)

    # create a different test for every entry in tool_list
    if 'tool_list' in metafunc.funcargnames:
        metafunc.parametrize('tool_list', tool_list)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    '''
        We are using pytest hook to generate logs.
        Pytest gives an access to the executing environment,
        by implementing a hook to it, we can generate custom test reports.
        In this case : we log the failing test as error
        @item : is an test run object
    '''
    # run the test first
    outcome = yield
    # result env for the test
    rep = outcome.get_result()
    # log on call, not on setup/teardown
    if rep.when == "call":
        # get logger
        logger = logging.getLogger('JAVA8_Tests')
        # write when handler is a file
        if len(logger.handlers) > 0 and\
                isinstance(logger.handlers[0], logging.FileHandler):
            # custom message to log test name, status and parameter
            message = 'Test --> %s -- status --> %s -- param --> %s' % \
                (item.__dict__['name'], rep.outcome,\
                item.__dict__['funcargs'])
            # if test failed log it as error
            if rep.failed:
                logger.error(message)
            # if test passed log it as info
            else:
                logger.info(message)
