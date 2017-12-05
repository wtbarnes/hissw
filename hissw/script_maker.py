"""
Build SSW scripts from Jinja 2 templates
"""
import os
import datetime
import subprocess

from jinja2 import (Environment,
                    FileSystemLoader,
                    PackageLoader)
from scipy.io import readsav

from .read_config import defaults


class ScriptMaker(object):
    """
    Build and execute SSW IDL scripts.

    Parameters
    ----------
    ssw_packages : list
        List of SSW packages to load, e.g. 'sdo/aia', 'chianti'
    ssw_paths : list
        List of SSW paths to pass to `ssw_path`
    extra_paths : list
        Additional paths to add to the IDL namespace
    ssw_home : str
        Optional, root of SSW tree
    idl_home : str
        Optional, IDL executable
    hissw_home : str
        Optional, where to save temp files
    """

    def __init__(self, ssw_packages=None, ssw_paths=None, extra_paths=None,
                 ssw_home=None, idl_home=None, hissw_home=None):
        self.ssw_packages = ssw_packages if ssw_packages is not None else []
        self.ssw_paths = ssw_paths if ssw_paths is not None else []
        self.extra_paths = extra_paths if extra_paths is not None else []
        self.env = Environment(loader=PackageLoader('hissw', 'templates'))
        self.setup_home(ssw_home, idl_home, hissw_home)

    def setup_home(self, ssw_home, idl_home, hissw_home):
        """
        Setup SSW, IDL, and hissw home locations
        """
        self.ssw_home = defaults['ssw_home'] if ssw_home is None else ssw_home
        if self.ssw_home is None:
            raise ValueError('''ssw_home must be set at instantiation or in the hisswrc file.''')
        self.idl_home = defaults['idl_home'] if idl_home is None else idl_home
        if self.idl_home is None:
            raise ValueError('''idl_home must be set at instantiation or in the hisswrc file.''')
        self.hissw_home = defaults['hissw_home'] if hissw_home is None else hissw_home
        if self.hissw_home is None:
            raise ValueError('''hissw_home must be set at instantiation or in the hisswrc file.''')

    def _build_custom_scripts(self, script, args):
        """
        Generate custom IDL scripts from templates
        """
        if os.path.isfile(script):
            env = Environment(loader=FileSystemLoader(os.path.dirname(script)))
            idl_script = env.get_template(os.path.basename(script)).render(**args)
        else:
            env = Environment()
            idl_script = env.from_string(script).render(**args)

        return idl_script

    def _build_command_script(self, script, save_vars, save_filename, command_filename):
        """
        Generate parent IDL script
        """
        if save_vars is None:
            save_vars = []
        params = {'ssw_paths': self.ssw_paths, 'extra_paths': self.extra_paths, 'script': script,
                  'save_vars': save_vars, 'save_filename': save_filename}
        idl_commands = self.env.get_template('parent.pro').render(**params)
        with open(command_filename, 'w') as f:
            f.write(idl_commands)

    def _build_shell_script(self, command_filename, shell_filename):
        """
        Generate shell script for starting up SSWIDL
        """
        params = {'ssw_home': self.ssw_home, 'ssw_packages': self.ssw_packages,
                  'idl_home': self.idl_home, 'command_filename': command_filename}
        shell_script = self.env.get_template('startup.sh').render(**params)
        with open(shell_filename, 'w') as f:
            f.write(shell_script)

    def run(self, script, args=None, save_vars=None, cleanup=True, verbose=True):
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
        cleanup : bool, optional
            Delete temporary shell and .sav files
        verbose : bool, optional
        """
        args = {} if args is None else args
        # generate filename for IDL sav file
        fn_template = os.path.join(self.hissw_home, '{name}_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.{ext}')
        save_filename = fn_template.format(name='idl_vars', ext='sav')
        command_filename = fn_template.format(name='idl_script', ext='pro')
        shell_filename = fn_template.format(name='ssw_shell', ext='sh')
        # generate custom scripts
        idl_script = self._build_custom_scripts(script, args)
        # generate commands and save to file
        self._build_command_script(idl_script, save_vars, save_filename, command_filename)
        # generate shell script
        self._build_shell_script(command_filename, shell_filename)
        # run the shell script
        subprocess.call(['chmod', 'u+x', shell_filename])
        try:
            cmd_output = subprocess.check_output(shell_filename, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            print(exc.output)
        else:
            if verbose:
                print(cmd_output.decode('utf-8'))
        # get results from save file
        results = readsav(save_filename)
        # delete scripts
        if cleanup:
            subprocess.call(['rm', command_filename])
            subprocess.call(['rm', shell_filename])
            subprocess.call(['rm', save_filename])

        return results
