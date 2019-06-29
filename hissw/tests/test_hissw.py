"""
Module level tests
"""
import pytest
import hissw
from hissw.util import SSWIDLError

run_kwargs = {'verbose': True}


@pytest.fixture
def hissw_env_blank():
    return hissw.Environment()


def test_exception(hissw_env_blank):
    """
    Test exception catching
    """
    with pytest.raises(SSWIDLError):
        _ = hissw_env_blank.run('foobar', **run_kwargs)


def test_no_args_no_ssw(hissw_env_blank):
    """
    No input arguments and no calls to SSW functions
    """
    script = '''
    n = 5
    i = REBIN(LINDGEN(n), n, n)
    j = REBIN(TRANSPOSE(LINDGEN(n)), n, n)
    array = (i GE j)
    '''
    results = hissw_env_blank.run(script, **run_kwargs)
    assert results['array'].shape == (5, 5)


def test_no_ssw(hissw_env_blank):
    """
    No calls to SSW functions
    """
    script = '''
    n = {{ n }}
    i = REBIN(LINDGEN(n), n, n)           
    j = REBIN(TRANSPOSE(LINDGEN(n)), n, n)
    array = (i GE j)
    '''
    n = 100
    results = hissw_env_blank.run(script, args={'n': n}, **run_kwargs)
    assert results['array'].shape == (n, n)


def test_aia_response_functions():
    """
    Compute AIA response functions using AIA packages in SSW
    """
    script = '''response = aia_get_response(/{{ flags | join(',/') }})
    ; Pull needed elements out of structure
    logt = response.logte
    resp94 = response.a94.tresp
    resp131 = response.a131.tresp
    resp171 = response.a171.tresp
    resp193 = response.a193.tresp
    resp211 = response.a211.tresp
    resp335 = response.a335.tresp
    '''
    args = {'flags': ['temp', 'dn', 'timedepend_date', 'evenorm']}
    hissw_env = hissw.Environment(ssw_packages=['sdo/aia'], ssw_paths=['aia'])
    results = hissw_env.run(script, args=args, **run_kwargs)
    assert 'resp94' in results
    assert 'resp131' in results
    assert 'resp171' in results
    assert 'resp193' in results
    assert 'resp211' in results
    assert 'resp335' in results
    assert results['resp94'].shape == results['logt'].shape
    assert results['resp131'].shape == results['logt'].shape
    assert results['resp171'].shape == results['logt'].shape
    assert results['resp193'].shape == results['logt'].shape
    assert results['resp211'].shape == results['logt'].shape
    assert results['resp335'].shape == results['logt'].shape
