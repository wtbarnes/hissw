"""
Module level tests
"""
import os

import astropy.units as u
import jinja2
import numpy as np
import pytest

import hissw
from hissw.filters import log10_filter, units_filter
from hissw.util import IDLNotFoundError, SSWIDLError, SSWNotFoundError


@pytest.fixture
def idl_env(idl_home):
    env = hissw.Environment(idl_home=idl_home, idl_only=True)
    try:
        _ = env.run('')
    except IDLNotFoundError:
        pytest.skip(f'Skipping IDL tests. No IDL installation found at {env.idl_home}.')
    else:
        return env

@pytest.fixture
def ssw_env(idl_env, ssw_home):
    env = hissw.Environment(idl_home=idl_env.idl_home,
                            ssw_home=ssw_home,
                            ssw_packages=['sdo/aia'],
                            ssw_paths=['aia'])
    try:
        _ = env.run('')
    except SSWNotFoundError:
        pytest.skip(f'Skipping SSW tests. No SSW installation found at {env.ssw_home}.')
    else:
        return env


@pytest.fixture
def render_env():
    # For tests that build scripts but never start IDL
    return hissw.Environment(idl_home='/not/used', idl_only=True)


def test_rendered_scripts():
    env = hissw.Environment(idl_home='/idl', ssw_home='/ssw',
                            ssw_packages=['sdo/aia', 'chianti'], ssw_paths=['aia', 'xrt'],
                            extra_paths=['/my/code'])
    shell = env.shell_script('command.pro')
    assert 'setenv SSW /ssw\n' in shell
    assert 'setenv SSW_INSTR "sdo/aia chianti"\n' in shell
    assert 'setenv IDL_DIR /idl\n' in shell
    assert 'sswidl command.pro' in shell
    command = env.command_script('procedure.pro')
    assert 'ssw_path,/aia, /xrt\n' in command
    assert "!PATH=EXPAND_PATH('/my/code')+':'+!PATH\n" in command
    assert '.run procedure.pro\n' in command
    assert "save,a,b,filename='out.sav'" in env.procedure_script('a = 1', ['a', 'b'], 'out.sav')
    assert "save,filename='out.sav'" in env.procedure_script('a = 1', [], 'out.sav')


def test_exception_idl_command(idl_env):
    """
    Test exception catching
    """
    with pytest.raises(SSWIDLError):
        _ = idl_env.run('foobar')


def test_exception_missing_ssw(tmp_path):
    env = hissw.Environment(idl_home=tmp_path, ssw_home=tmp_path)
    with pytest.raises(SSWNotFoundError):
        _ = env.run('')


def test_exception_missing_idl(tmp_path):
    env = hissw.Environment(idl_home=tmp_path, idl_only=True)
    with pytest.raises(IDLNotFoundError):
        _ = env.run('')


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
    results = idl_env.run(script)
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
    results = idl_env.run(script, args={'n': n})
    assert results['array'].shape == (n, n)


@pytest.mark.parametrize(('log_level', 'log_record_length'), [
    ('DEBUG', 5),
    ('INFO', 2),
    ('WARNING', 1),
])
def test_logging(idl_env, caplog, log_level, log_record_length):
    caplog.set_level(log_level)
    _ = idl_env.run('print, "Hello World"')
    assert len(caplog.records) == log_record_length


def test_non_utf8_output(idl_env):
    # 197B is a Latin-1 Angstrom sign, which is not valid UTF-8
    res = idl_env.run("a = 1\nprint, string(197B)")
    assert res['a'] == 1


def test_idl_cannot_read_our_stdin(idl_env):
    # Put a line on our stdin. If IDL inherited it, `read` would succeed.
    read_end, write_end = os.pipe()
    os.write(write_end, b'hello\n')
    os.close(write_end)
    original_stdin = os.dup(0)
    os.dup2(read_end, 0)
    try:
        with pytest.raises(SSWIDLError, match='End of file encountered'):
            idl_env.run("x = ''\nread, x")
    finally:
        os.dup2(original_stdin, 0)
        os.close(original_stdin)
        os.close(read_end)


def test_no_results_raises(idl_env):
    # An early return does not print "execution halted", but nothing is saved
    with pytest.raises(SSWIDLError, match='IDL did not save any results'):
        idl_env.run("a = 1\nreturn")


def test_missing_argument_raises(render_env):
    with pytest.raises(jinja2.UndefinedError, match="'a' is undefined"):
        render_env.render_script('foo = {{ a }} + 1', {'A': 5})


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
    results = ssw_env.run(script, args=args)
    for c  in [94, 131, 171, 193, 211, 335]:
        assert f'resp{c}' in results
        assert results[f'resp{c}'].shape == results['logt'].shape


def test_units_filter(idl_env):
    script = """
    foo = {{ foo | to_unit('K') }}
    """
    res = idl_env.run(script, args={'foo': 1*u.MK})
    assert np.allclose(res['foo'], 1e6)


def test_units_filter_exception(render_env):
    script = """
    foo = {{ foo | to_unit('K') }}
    """
    with pytest.raises(u.UnitsError,
                       match='Value must be a quantity with units compatible with K'):
        _ = render_env.render_script(script, {'foo': 1})


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


def test_filters_render_arrays_as_valid_idl():
    assert str(units_filter([1, 2]*u.MK, 'K')) == '[1000000.0, 2000000.0]'
    assert str(log10_filter([1e6, 1e7])) == '[6.0, 7.0]'


def test_log10_filter_array(idl_env):
    res = idl_env.run('foo = {{ foo | log10 }}', args={'foo': [1e6, 1e7]})
    assert np.allclose(res['foo'], [6, 7])


def test_string_list_filter(idl_env):
    script = """
    foo = [{{ foo | string_list | join(',') }}]
    """
    foo = ['my', 'list', 'of', 'strings']
    res = idl_env.run(script, args={'foo': foo})
    assert [v.decode('utf-8') for v in res['foo']] == foo


def test_default_ssw_var(ssw_env):
    script = """
    foo = '{{ ssw_home }}'
    """
    res = ssw_env.run(script)
    assert res['foo'].decode('utf-8') == str(ssw_env.ssw_home)


def test_forced_colour_not_passed_to_idl(idl_env, monkeypatch):
    # See https://github.com/wtbarnes/hissw/issues/37
    monkeypatch.setenv('CLICOLOR_FORCE', '1')
    monkeypatch.setenv('FORCE_COLOR', '1')
    res = idl_env.run('''
    clicolor_force = getenv('CLICOLOR_FORCE')
    force_color = getenv('FORCE_COLOR')
    ''')
    assert not res['clicolor_force']
    assert not res['force_color']


def test_script_from_file(idl_env, tmp_path):
    script = '''foo = {{a}} + {{b}}'''
    script_file = tmp_path / 'test_script.pro'
    with open(script_file, 'w') as f:
        f.write(script)
    a = 1
    b = 2
    result = idl_env.run(script_file, args={'a':a, 'b': b})
    assert result['foo'] == (a + b)


def test_custom_filters(idl_env):
    filters = {
        'my_filter': lambda x: 'foo' if x < 0.5 else 'bar'
    }
    env = hissw.Environment(idl_home=idl_env.idl_home, idl_only=True, filters=filters)
    script = '''
    a = '{{ a | my_filter }}'
    b = '{{ b | my_filter }}'
    '''
    args = {'a': 0.1, 'b': 0.6}
    result = env.run(script, args=args)
    assert result['a'].decode('utf-8') == filters['my_filter'](args['a'])
    assert result['b'].decode('utf-8') == filters['my_filter'](args['b'])


def test_invalid_script(render_env):
    with pytest.raises(ValueError, match='Input script must either be a string or path to a script.'):
        _ = render_env.render_script(None, {})


def test_custom_header_footer(idl_env):
    header = 'foo = {{ a }}'
    footer = 'bar = {{ a }} + {{ b }}'
    env_custom = hissw.Environment(idl_home=idl_env.idl_home, idl_only=True,
                                   header=header, footer=footer)
    script = '''
    print, {{ a }}
    print, {{ b }}
    '''
    args = {'a': 1, 'b': 2}
    result = env_custom.run(script, args=args)
    assert result['foo'] == args['a']
    assert result['bar'] == args['a'] + args['b']


@pytest.mark.parametrize('var', [
    1 / 3,
    float(10),
    [1/3, 1/7, 0.1],
    np.random.rand(100),
    list(np.random.rand(10).astype(np.longdouble))
])
def test_force_double_precision_filter(var, idl_env):
    # This test ensures that floating point precision is conserved when passing
    # things from Python to IDL. See https://github.com/wtbarnes/hissw/issues/31
    result = idl_env.run(
            '''
            var = {{ var | force_double_precision }}
            var_size = size(var)
            ''',
            args={'var': var})
    assert u.allclose(var, result['var'], atol=0.0, rtol=0.0)
    # The result of IDL size has a variable number of entries depending on the
    # dimensionality of the input array
    # NOTE: 5 corresponds to double-precision floating point. See
    # https://www.l3harrisgeospatial.com/docs/make_array.html#TYPE
    assert result['var_size'][len(result['var'].shape) + 1] == 5


@pytest.mark.parametrize('var', [
    1 / 3 * u.s,
    float(10) * u.s,
    [1/3, 1/7, 0.1] * u.s,
    np.random.rand(100) * u.minute,
])
def test_force_double_precision_filter_with_quantity(var, idl_env):
    # This test ensures that floating point precision is conserved when passing
    # things from Python to IDL. See https://github.com/wtbarnes/hissw/issues/31
    result = idl_env.run('var = {{ var | to_unit("h") | force_double_precision }}',
                         args={'var': var})
    assert u.allclose(var.to_value('h'), result['var'], atol=0.0, rtol=0.0)
