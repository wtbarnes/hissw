"""
Test setup
"""
import pytest

import hissw


def pytest_addoption(parser):
    parser.addoption('--idl-home', action='store', default=None,
                     help='Path to top level IDL directory')
    parser.addoption('--ssw-home', action='store', default=None,
                     help='Path to top of SSW tree')


def _path_or_skip(request, name):
    # Skip rather than error, so the tests that need no IDL can run anywhere
    option = '--' + name.replace('_', '-')
    path = request.config.getoption(option)
    if path is None and hissw.defaults.get(name) is None:
        pytest.skip(f'Needs {option} or {name} set in the hisswrc file.')
    return path


@pytest.fixture
def idl_home(request):
    return _path_or_skip(request, 'idl_home')


@pytest.fixture
def ssw_home(request):
    return _path_or_skip(request, 'ssw_home')
