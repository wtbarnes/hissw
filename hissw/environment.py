"""
Build SSW scripts from Jinja 2 templates
"""
import os
import datetime
import pathlib
import subprocess
import tempfile

import jinja2
from scipy.io import readsav
from .filters import string_list_filter

from .read_config import defaults
from .util import SSWIDLError, IDLLicenseError
from .filters import *


class Environment(object):
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
        self.ssw_packages = ssw_packages if ssw_packages is not None else []
        self.ssw_paths = ssw_paths if ssw_paths is not None else []
        self.extra_paths = extra_paths if extra_paths is not None else []
        self.env = jinja2.Environment(loader=jinja2.PackageLoader('hissw', 'templates'))
        self.env.filters['to_unit'] = units_filter
        self.env.filters['log10'] = log10_filter
        self.env.filters['string_list'] = string_list_filter
        if filters is not None:
            for k, v in filters.items():
                self.env.filters[k] = v
        self.header = '' if header is None else header
        self.footer = '' if footer is None else footer
        self._setup_home(ssw_home, idl_home, idl_only=idl_only)

    def _setup_home(self, ssw_home, idl_home, idl_only=False):
        """
        Setup SSW and IDL home locations
        """
        self.ssw_home = defaults.get('ssw_home') if ssw_home is None else ssw_home
        if idl_only:
            self.ssw_home = None
        else:
            if self.ssw_home is None:
                raise ValueError('ssw_home must be set at instantiation or in the hisswrc file.')
        self.idl_home = defaults.get('idl_home') if idl_home is None else idl_home
        if self.idl_home is None:
            raise ValueError('idl_home must be set at instantiation or in the hisswrc file.')

    @property
    def executable(self):
        """
        Path to executable for running code
        """
        if self.ssw_home:
            return 'sswidl'
        else:
            return os.path.join(self.idl_home, 'bin', 'idl')

    def render_script(self, script, args):
        """
        Render custom IDL scripts from templates and input arguments
        """
        if isinstance(script, (str, pathlib.Path)) and os.path.isfile(script):
            with open(script, 'r') as f:
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
        if save_vars is None:
            save_vars = []
        params = {'_script': script,
                  '_save_vars': save_vars,
                  '_save_filename': save_filename}
        return self.env.get_template('procedure.pro').render(**params)

    def command_script(self, procedure_filename):
        """
        Generate parent IDL script
        """
        params = {'ssw_paths': self.ssw_paths,
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
                  'command_filename': command_filename}
        return self.env.get_template('startup.sh').render(**params)

    def run(self, script, args=None, save_vars=None, verbose=True, **kwargs):
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
        verbose : bool, optional
            If True, print STDERR and SDOUT. Otherwise it will be
            suppressed. This is useful for debugging.
        """
        args = {} if args is None else args
        # Expose the ssw_home variable in all scripts by default
        args.update({'ssw_home': self.ssw_home})
        with tempfile.TemporaryDirectory() as tmpdir:
            # Get filenames
            fn_template = os.path.join(
                tmpdir, '{name}_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.{ext}')
            save_filename = fn_template.format(name='idl_vars', ext='sav')
            procedure_filename = fn_template.format(name='idl_procedure', ext='pro')
            command_filename = fn_template.format(name='idl_script', ext='pro')
            shell_filename = fn_template.format(name='ssw_shell', ext='sh')
            # Render and save scripts
            idl_script = self.custom_script(script, args)
            with open(procedure_filename, 'w') as f:
                f.write(self.procedure_script(idl_script, save_vars, save_filename))
            with open(command_filename, 'w') as f:
                f.write(self.command_script(procedure_filename))
            with open(shell_filename, 'w') as f:
                f.write(self.shell_script(command_filename,))
            # Execute
            subprocess.call(['chmod', 'u+x', shell_filename])
            cmd_output = subprocess.run([shell_filename], shell=True, stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
            self._check_for_errors(cmd_output, verbose, **kwargs)
            results = readsav(save_filename)

        return results

    def _check_for_errors(self, output, verbose, **kwargs):
        """
        Check IDL output to try and decide if an error has occurred
        """
        stdout = output.stdout.decode('utf-8')
        stderr = output.stderr.decode('utf-8')
        # NOTE: For some reason, not only errors are output to stderr so we
        # have to check it for certain keywords to see if an error occurred
        if kwargs.get('raise_exceptions', True):
            if 'execution halted' in stderr.lower():
                raise SSWIDLError(stderr)
            if 'failed to acquire license' in stderr.lower():
                raise IDLLicenseError(stderr)
        if verbose:
            print(f'{stderr}\n{stdout}')
