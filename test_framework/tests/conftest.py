'''
    Create configuration for test
    This propagates for all the subfolder
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

    if  metafunc.config.option.tool and\
            metafunc.config.option.tool_path:

        if isinstance(metafunc.config.option.tool, str):
            tool_list = [
                metafunc.config.option.tool,
                metafunc.config.option.tool_path
            ]
        elif isinstance(metafunc.config.option.tool, list):
            tool_list = zip(metafunc.config.option.tool,
                metafunc.config.option.tool_path)

    if metafunc.config.option.conf_file:
        try:
            with open(metafunc.config.option.conf_file, 'r') as fread:
                tool_list = json.load(fread)
        except:
            tool_list = []

    # create combination of tools * apps
    if 'comb' in metafunc.funcargnames:
        tool_app_pair = [tup for tup in\
                itertools.product(tool_list, pytest.apps_list)]
        metafunc.parametrize('comb', tool_app_pair)

    if 'tool_list' in metafunc.funcargnames:
        metafunc.parametrize('tool_list', tool_list)
