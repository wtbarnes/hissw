"""
Build SSW scripts from Jinja 2 templates
"""
import datetime
import os
import pathlib
import platform
import stat
import subprocess
import tempfile

import jinja2
from scipy.io import readsav

from hissw.filters import (force_double_precision_filter, log10_filter,
                           string_list_filter, units_filter)
from hissw.read_config import defaults
from hissw.util import (IDLLicenseError, IDLNotFoundError, SSWIDLError,
                        SSWNotFoundError)


class Environment:
    """
    Environment for running SSW and IDL scripts

    Parameters
    ----------
    ssw_packages : `list`, optional
        List of SSW packages to load, e.g. 'sdo/aia', 'chianti'
    ssw_paths : `list`, optional
        List of SSW paths to pass to `ssw_path`
    extra_paths : `list`, optional
        Additional paths to add to the IDL namespace. Note that these
        are appended to the front of the path such that they take
        precedence over the existing path.
    ssw_home : `str`, optional
        Root of SSW tree
    idl_home : `str`, optional
        Path to IDL executable
    filters : `dict`, optional
        Filters to use in scripts. This should be a dictionary where the key
        is the name of the filter and the value is the corresponding
        function.
    idl_only : `bool`, optional
        If True, do not do any setup associated with SSW. This is useful
        if your script has no SSW dependence.
    header_script : `str` or path-like, optional
        Script to run before script passed to ``run`` method. Can use any
        of the variables passed to ``run``.
    footer_script : `str` or path-like, optional
        Script to run after script passed to ``run`` method. Can use any
        of the variables passed to ``run``.
    """

    def __init__(self, ssw_packages=None, ssw_paths=None, extra_paths=None,
                 ssw_home=None, idl_home=None, filters=None, idl_only=False,
                 header=None, footer=None):
        # NOTE: Import here to avoid circular imports
        from hissw import log
        self.log = log
        self.idl_only = idl_only
        self.ssw_home = ssw_home
        self.idl_home = idl_home
        self.ssw_packages = ssw_packages if ssw_packages is not None else []
        self.ssw_paths = ssw_paths if ssw_paths is not None else []
        self.extra_paths = extra_paths if extra_paths is not None else []
        self.env = jinja2.Environment(loader=jinja2.PackageLoader('hissw', 'templates'))
        self._setup_filters(filters)
        self.header = '' if header is None else header
        self.footer = '' if footer is None else footer

    def _setup_filters(self, filters):
        self.env.filters['to_unit'] = units_filter
        self.env.filters['log10'] = log10_filter
        self.env.filters['string_list'] = string_list_filter
        self.env.filters['force_double_precision'] = force_double_precision_filter
        if filters is not None:
            for k, v in filters.items():
                self.env.filters[k] = v

    @property
    def ssw_home(self):
        return self._ssw_home

    @ssw_home.setter
    def ssw_home(self, value):
        self._ssw_home = defaults.get('ssw_home') if value is None else value
        try:
            self._ssw_home = pathlib.Path(self._ssw_home)
        except TypeError:
            if not self.idl_only:
                raise ValueError('ssw_home must be set at instantiation or in the hisswrc file.')

    @property
    def idl_home(self):
        return self._idl_home

    @idl_home.setter
    def idl_home(self, value):
        self._idl_home = defaults.get('idl_home') if value is None else value
        try:
            self._idl_home = pathlib.Path(self._idl_home)
        except TypeError:
            raise ValueError('idl_home must be set at instantiation or in the hisswrc file.')

    @property
    def executable(self):
        """
        Path to executable for running code
        """
        if self.idl_only:
            return self.idl_home / 'bin' / 'idl'
        else:
            return 'sswidl'

    def render_script(self, script, args):
        """
        Render custom IDL scripts from templates and input arguments
        """
        if isinstance(script, (str, pathlib.Path)) and pathlib.Path(script).is_file():
            with open(script) as f:
                script = f.read()
        if not isinstance(script, str):
            raise ValueError('Input script must either be a string or path to a script.')
        return self.env.from_string(script).render(**args)

    def custom_script(self, script, args):
        """
        Generate the script that will be executed
        """
        body = self.render_script(script, args)
        header = self.render_script(self.header, args)
        footer = self.render_script(self.footer, args)
        idl_script = f'{header}\n{body}\n{footer}'
        return idl_script

    def procedure_script(self, script, save_vars, save_filename):
        """
        Render inner procedure file
        """
        params = {'_script': script,
                  '_save_vars': save_vars,
                  '_save_filename': save_filename}
        return self.env.get_template('procedure.pro').render(**params)

    def command_script(self, procedure_filename):
        """
        Generate parent IDL script
        """
        params = {'ssw_paths': self.ssw_paths,
                  'use_ssw': not self.idl_only,
                  'extra_paths': self.extra_paths,
                  'procedure_filename': procedure_filename}
        return self.env.get_template('parent.pro').render(**params)

    def shell_script(self, command_filename):
        """
        Generate shell script for starting up SSWIDL
        """
        params = {'executable': self.executable,
                  'ssw_home': self.ssw_home,
                  'ssw_packages': self.ssw_packages,
                  'idl_home': self.idl_home,
                  'use_ssw': not self.idl_only,
                  'command_filename': command_filename}
        return self.env.get_template('startup.sh').render(**params)

    def run(self, script, args=None, save_vars=None, raise_exceptions=True):
        """
        Set up the SSWIDL environment and run the supplied scripts.

        Parameters
        ----------
        script : str
            Literal script or path to script file
        args : dict, optional
            Input arguments to script
        save_vars : list, optional
            Variables to save and return from the IDL namespace
        raise_exceptions : bool, optional
            If True, raise an exception based on the IDL output. This is left
            as a flag because not raising an exception is sometimes useful
            for debugging.
        """
        save_vars = [] if save_vars is None else save_vars
        args = {} if args is None else args
        # Expose the ssw_home variable in all scripts by default
        args.update({'ssw_home': self.ssw_home})
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir) / 'hissw_files'
            tmpdir_path.mkdir(parents=True, exist_ok=True)
            date_string = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            # Construct temporary filenames
            save_filename = tmpdir_path / f'idl_vars_{date_string}.sav'
            procedure_filename = tmpdir_path / f'idl_procedure_{date_string}.pro'
            command_filename = tmpdir_path / f'idl_script_{date_string}.pro'
            shell_filename = tmpdir_path / f'ssw_shell_{date_string}.sh'
            # Render and write scripts
            idl_script = self.custom_script(script, args)
            files = [
                (procedure_filename, self.procedure_script(idl_script, save_vars, save_filename)),
                (command_filename, self.command_script(procedure_filename)),
                (shell_filename, self.shell_script(command_filename)),
            ]
            for filename, filescript in files:
                self.log.debug(f'{filename}:\n{filescript}')
                with open(filename, 'w') as f:
                    f.write(filescript)
            # Execute
            self._run_shell_script(shell_filename, raise_exceptions)
            results = readsav(save_filename)

        return results

    def _run_shell_script(self, path, raise_exceptions):
        os.chmod(path, mode=stat.S_IRWXU)
        on_windows = platform.system().lower() == 'windows'
        cmd_output = subprocess.run(
            path.name if on_windows else f'./{path.name}',
            cwd=path.parent,
            shell=True,
            capture_output=True,
            text=True,
        )
        self._check_for_errors(cmd_output, raise_exceptions=raise_exceptions)

    def _check_for_errors(self, output, raise_exceptions=True):
        """
        Check IDL output to try and decide if an error has occurred
        """
        stdout = output.stdout
        stderr = output.stderr
        # NOTE: For some reason, not only errors are output to stderr so we
        # have to check it for certain keywords to see if an error occurred
        if raise_exceptions:
            if 'execution halted' in stderr.lower():
                raise SSWIDLError(stderr)
            if 'failed to acquire license' in stderr.lower():
                raise IDLLicenseError(stderr)
            if 'setup.ssw: no such file or directory' in stderr.lower():
                raise SSWNotFoundError(f'No SSW installation found at {self.ssw_home}.')
            if 'idl: command not found' in stderr.lower():
                raise IDLNotFoundError(f'No IDL installation found at {self.idl_home}.')
        self.log.warning(stderr)
        self.log.info(stdout)
