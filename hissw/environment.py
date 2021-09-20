"""
Build SSW scripts from Jinja 2 templates
"""
import os
import datetime
import subprocess
import tempfile

from jinja2 import (Environment as Env,
                    FileSystemLoader,
                    PackageLoader)
from scipy.io import readsav

from .read_config import defaults
from .util import SSWIDLError, IDLLicenseError


class Environment(object):
    """
    Environment for running SSW and IDL scripts

    Parameters
    ----------
    ssw_packages : list, optional
        List of SSW packages to load, e.g. 'sdo/aia', 'chianti'
    ssw_paths : list, optional
        List of SSW paths to pass to `ssw_path`
    extra_paths : list, optional
        Additional paths to add to the IDL namespace. Note that these
        are appended to the front of the path such that they take
        precedence over the existing path.
    ssw_home : str, optional
        Root of SSW tree
    idl_home : str, optional
        Path to IDL executable
    """

    def __init__(self, ssw_packages=None, ssw_paths=None, extra_paths=None,
                 ssw_home=None, idl_home=None,):
        self.ssw_packages = ssw_packages if ssw_packages is not None else []
        self.ssw_paths = ssw_paths if ssw_paths is not None else []
        self.extra_paths = extra_paths if extra_paths is not None else []
        self.env = Env(loader=PackageLoader('hissw', 'templates'))
        self._setup_home(ssw_home, idl_home,)

    def _setup_home(self, ssw_home, idl_home,):
        """
        Setup SSW and IDL home locations
        """
        self.ssw_home = defaults['ssw_home'] if ssw_home is None else ssw_home
        if self.ssw_home is None:
            raise ValueError('''ssw_home must be set at instantiation or in the hisswrc file.''')
        self.idl_home = defaults['idl_home'] if idl_home is None else idl_home
        if self.idl_home is None:
            raise ValueError('''idl_home must be set at instantiation or in the hisswrc file.''')

    def custom_script(self, script, args):
        """
        Generate custom IDL scripts from templates
        """
        if os.path.isfile(script):
            env = Env(loader=FileSystemLoader(os.path.dirname(script)))
            idl_script = env.get_template(os.path.basename(script)).render(**args)
        else:
            env = Env()
            idl_script = env.from_string(script).render(**args)

        return idl_script

    def procedure_script(self, script, save_vars, save_filename):
        """
        Render inner procedure file
        """
        if save_vars is None:
            save_vars = []
        params = {'script': script, 'save_vars': save_vars, 'save_filename': save_filename}
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
        params = {'ssw_home': self.ssw_home,
                  'ssw_packages': self.ssw_packages,
                  'idl_home': self.idl_home,
                  'command_filename': command_filename}
        return self.env.get_template('startup.sh').render(**params)

    def run(self, script, args=None, save_vars=None, verbose=True):
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
            self._check_for_errors(cmd_output, verbose)
            results = readsav(save_filename)

        return results

    def _check_for_errors(self, output, verbose):
        """
        Check IDL output to try and decide if an error has occurred
        """
        stdout = output.stdout.decode('utf-8')
        stderr = output.stderr.decode('utf-8')
        # NOTE: For some reason, not only errors are output to stderr so we
        # have to check it for certain keywords to see if an error occurred
        if 'execution halted' in stderr.lower():
            raise SSWIDLError(stderr)
        if 'failed to acquire license' in stderr.lower():
            raise IDLLicenseError(stderr)
        if verbose:
            print(f'{stderr}\n{stdout}')
