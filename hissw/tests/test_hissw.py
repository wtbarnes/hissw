"""
Module level tests
"""
import numpy as np
import pytest
import hissw


@pytest.fixture
def hissw_env_blank():
    return hissw.ScriptMaker()


def test_no_args_no_ssw(hissw_env_blank):
    """
    No input arguments and no calls to SSW functions
    """
    script = '''
n = 5
i = REBIN(LINDGEN(n), n, n)           
j = REBIN(TRANSPOSE(LINDGEN(n)), n, n)
array = (i GE j)'''
    results = hissw_env_blank.run(script)
    assert results['array'].shape == (5, 5)


def test_no_ssw(hissw_env_blank):
    """
    No calls to SSW functions
    """
    script = '''
n = {{ n }}
i = REBIN(LINDGEN(n), n, n)           
j = REBIN(TRANSPOSE(LINDGEN(n)), n, n)
array = (i GE j)'''
    n = 100
    results = hissw_env_blank.run(script, args={'n': n})
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
; Interpolate
interp_logt = {{ interp_logt }}
interp_resp94 = interpol(resp94,logte,interp_logte)
interp_resp131 = interpol(resp131,logte,interp_logte)
interp_resp171 = interpol(resp171,logte,interp_logte)
interp_resp193 = interpol(resp193,logte,interp_logte)
interp_resp211 = interpol(resp211,logte,interp_logte)
interp_resp335 = interpol(resp335,logte,interp_logte)'''
    interp_logt = np.linspace(5, 8, 1000)
    flags = ['temp', 'dn', 'timedepend_date', 'evenorm']
    args = {'flags': flags, 'interp_logt': interp_logt.tolist()}
    hissw_env = hissw.ScriptMaker(ssw_packages=['sdo/aia'], ssw_paths=['aia'])
    results = hissw_env.run(script, args=args, verbose=True, cleanup=False)
    assert 'interp_resp94' in results
    assert 'interp_resp131' in results
    assert 'interp_resp171' in results
    assert 'interp_resp193' in results
    assert 'interp_resp211' in results
    assert 'interp_resp335' in results
    assert results['interp_resp94'].shape == interp_logt.shape
    assert results['interp_resp131'].shape == interp_logt.shape
    assert results['interp_resp171'].shape == interp_logt.shape
    assert results['interp_resp193'].shape == interp_logt.shape
    assert results['interp_resp211'].shape == interp_logt.shape
    assert results['interp_resp335'].shape == interp_logt.shape
