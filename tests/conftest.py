'''
    Performs automatic test discovery using fixtures. Creates two dynamic fixtures
    and uses them to generate a test for every tool and every application.
    Tools are identified by a pair (tool, tool_path) where tool is the tool's
    name and tool_path specifies the path where the tool has been built and
    installed.
'''

import pytest
import itertools
import json
import logging
import os
import glob

def pytest_generate_tests(metafunc):
    '''
        Generate tests from combinations of fixtures
        for every tool and every app
    '''
    if 'adapter' in metafunc.fixturenames:
        # build tool_list as specified by --tool on the command line
        tool_list = metafunc.config.option.tool
        if not tool_list:
            tool_list = []
        elif not isinstance(tool_list, list):
            tool_list = [tool_list]
        
        # build tool_list as specified in the configuration file
        if metafunc.config.option.conf_file:
            try:
                with open(metafunc.config.option.conf_file, 'r') as fread:
                    tool_list = json.load(fread)
            except:
                tool_list = []

        # generate adapter fixture for every tool in tool_list
        metafunc.parametrize('adapter', tool_list,
            ids=[n for(n,_) in tool_list],
            indirect=True)

    # generate app fixture for every app
    if 'app' in metafunc.funcargnames:
        # case where app_list is passed on the command line
        app_list = metafunc.config.option.app
        # case where app_list is generated from contents of src/app/ directory
        if not app_list:
            app_list = [os.path.basename(x) for x in\
                         glob.glob(os.path.join(pytest.root_dir, 'src', 'apps', '*'))]
        elif isinstance(app_list, str):
            app_list = [app_list]
        metafunc.parametrize('app', app_list)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    '''
        Logging during the post-processing of a test run
        Ref: https://docs.pytest.org/en/latest/example/simple.html#post-process-test-reports-failures
        @item : test run object
    '''
    # execute all other hooks to obtain the report object
    outcome = yield
    # result env for the test
    rep = outcome.get_result()
    # log on call, not on setup/teardown
    if rep.when == "call":
        # get logger
        logger = logging.getLogger('JAVA8_Tests')
        # case where logging handler is a file
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
