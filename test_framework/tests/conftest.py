'''
    Create auto test discovery using fixtures, It create two dynamic fixtures
    1) comb: that is all combination of (tool, tool_path and apps)
    2) tool_list: list of tool,tool_path
    If user wants to run a parametrized tests for either combination
    the test evaluaters should use same fixture names
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
        # if a only one tool is passed
        if isinstance(metafunc.config.option.tool, str):
            tool_list = [
                metafunc.config.option.tool,
                metafunc.config.option.tool_path
            ]
        # if tool list
        elif isinstance(metafunc.config.option.tool, list):
            tool_list = zip(metafunc.config.option.tool,
                metafunc.config.option.tool_path)

    # read from a config file
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
