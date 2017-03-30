'''
    Create auto test discovery using fixtures
    pytest_generate_tests create a combination of different tests
        This create a new test for every entry in list,
        if we have tool -->[a,b] and apps -->[1,2]
        it will generate test [(a,1), (b,1), (a,2), (b,2)]
    To use it all test evaluators the test evaluator parameter should be
    1) comb : if you need (tool,too_path), app combination
    2) tool_list : if you need tool,tool_path combination
'''
import pytest
import itertools
import json

def pytest_generate_tests(metafunc):
    '''
        generate test from combinations
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
