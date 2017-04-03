'''
    Performs auto tests discovery using fixtures. Creates two dynamic fixtures
    and uses them to generate a test for every tool and every application.
    Tools are identified by a pair (tool, tool_path) where tool is the tool's
    name and tool_path specifies the path where the tool is found.

    TODO : Review
    If user wants to write a new parametrized tests using the fixtures,
    they should include the fixture as parameter to the test function signature.
    For example, if we want to use fixture : tool_list,
    the signature for new test should be   : test_bar(tool_list)
    This will create multiple new test depending on # of (tool, tool_path)
'''

import pytest
import itertools
import json

def pytest_generate_tests(metafunc):
    '''
        generate test from combinations from fixtures

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

    # create combination of tools * apps
    # for any function with parameter named 'comb'
    # create a new test with entry from combination
    if 'comb' in metafunc.funcargnames:
        tool_app_pair = [tup for tup in\
                itertools.product(tool_list, pytest.apps_list)]
        metafunc.parametrize('comb', tool_app_pair)

    # create a different test for every entry in tool_list
    if 'tool_list' in metafunc.funcargnames:
        metafunc.parametrize('tool_list', tool_list)
