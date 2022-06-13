"""
Test setup
"""
import pytest


def pytest_addoption(parser):
    parser.addoption('--idl-home', action='store', default=None,
                     help='Path to top level IDL directory')
    parser.addoption('--ssw-home', action='store', default=None,
                     help='Path to top of SSW tree')


@pytest.fixture
def idl_home(request):
    return request.config.getoption('--idl-home')


@pytest.fixture
def ssw_home(request):
    return request.config.getoption('--ssw-home')
