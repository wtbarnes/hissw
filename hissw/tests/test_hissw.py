"""
Module level tests
"""
import pytest
import hissw
import numpy as np
import astropy.units as u
from hissw.util import SSWIDLError

run_kwargs = {'verbose': True}


@pytest.fixture
def idl_env(idl_home):
    return hissw.Environment(idl_home=idl_home, idl_only=True)


@pytest.fixture
def ssw_env(idl_home, ssw_home):
    return hissw.Environment(idl_home=idl_home,
                             ssw_home=ssw_home,
                             ssw_packages=['sdo/aia'],
                             ssw_paths=['aia'])


def test_exception(idl_env):
    """
    Test exception catching
    """
    with pytest.raises(SSWIDLError):
        _ = idl_env.run('foobar', **run_kwargs)


def test_no_args(idl_env):
    """
    No input arguments and no calls to SSW functions
    """
    script = '''
    n = 5
    i = REBIN(LINDGEN(n), n, n)
    j = REBIN(TRANSPOSE(LINDGEN(n)), n, n)
    array = (i GE j)
    '''
    results = idl_env.run(script, **run_kwargs)
    assert results['array'].shape == (5, 5)


def test_with_args(idl_env):
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
    results = idl_env.run(script, args={'n': n}, **run_kwargs)
    assert results['array'].shape == (n, n)


def test_aia_response_functions(ssw_env):
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
    results = ssw_env.run(script, args=args, **run_kwargs)
    for c  in [94, 131, 171, 193, 211, 335]:
        assert f'resp{c}' in results
        assert results[f'resp{c}'].shape == results['logt'].shape


def test_units_filter(idl_env):
    script = """
    foo = {{ foo | to_unit('K') }}
    """
    res = idl_env.run(script, args={'foo': 1*u.MK})
    assert np.allclose(res['foo'], 1e6)


def test_units_filter_exception(idl_env):
    script = """
    foo = {{ foo | to_unit('K') }}
    """
    with pytest.raises(u.UnitsError,
                       match='Value must be a quantity with units compatible with K'):
        _= idl_env.run(script, args={'foo': 1})


def test_units_filter_array(idl_env):
    script = """
    foo = {{ foo | to_unit('K') | list }}
    """
    res = idl_env.run(script, args={'foo': [1, 2]*u.MK})
    assert np.allclose(res['foo'], [1e6, 2e6])


def test_log10_filter(idl_env):
    script = """
    foo = {{ foo | log10 }}
    """
    foo = 1e6
    res = idl_env.run(script, args={'foo': foo})
    assert res['foo'] == np.log10(foo)


def test_string_list_filter(idl_env):
    script = """
    foo = {{ foo | string_list }}
    """
    foo = ['my', 'list', 'of', 'strings']
    res = idl_env.run(script, args={'foo': foo})
    assert [v.decode('utf-8') for v in res['foo']] == [f"'{f}'" for f in foo]


def test_default_ssw_var(ssw_env):
    script = """
    foo = '{{ ssw_home }}'
    """
    res = ssw_env.run(script)
    assert res['foo'].decode('utf-8') == ssw_env.ssw_home


def test_script_from_file(idl_env, tmp_path):
    script = '''foo = {{a}} + {{b}}'''
    script_file = tmp_path / 'test_script.pro'
    with open(script_file, 'w') as f:
        f.write(script)
    a = 1
    b = 2
    result = idl_env.run(script_file, args={'a':a, 'b': b})
    assert result['foo'] == (a + b)


def test_custom_filters(idl_home):
    filters = {
        'my_filter': lambda x: 'foo' if x < 0.5 else 'bar'
    }
    env = hissw.Environment(idl_home=idl_home, idl_only=True, filters=filters)
    script = '''
    a = '{{ a | my_filter }}'
    b = '{{ b | my_filter }}'
    '''
    args = {'a': 0.1, 'b': 0.6}
    result = env.run(script, args=args)
    assert result['a'].decode('utf-8') == filters['my_filter'](args['a'])
    assert result['b'].decode('utf-8') == filters['my_filter'](args['b'])


def test_invalid_script(idl_env):
    with pytest.raises(ValueError, match='Input script must either be a string or path to a script.'):
        _ = idl_env.run(None)


def test_custom_header_footer(idl_home):
    header = 'foo = {{ a }}'
    footer = 'bar = {{ a }} + {{ b }}'
    env_custom = hissw.Environment(idl_home=idl_home, idl_only=True,
                                   header=header, footer=footer)
    script = '''
    print, {{ a }}
    print, {{ b }}
    '''
    args = {'a': 1, 'b': 2}
    result = env_custom.run(script, args=args)
    assert result['foo'] == args['a']
    assert result['bar'] == args['a'] + args['b']
