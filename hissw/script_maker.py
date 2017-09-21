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
    ssw_pkg_list : list
        List of SSW packages
    ssw_path_list : list
    ssw_home : str
    idl_home : str
    """

    def __init__(self, ssw_pkg_list=None, ssw_path_list=None, ssw_home=None, idl_home=None,
                 hissw_home=None, extra_paths=None):
        self.ssw_pkg_list = ssw_pkg_list if ssw_pkg_list is not None else []
        self.ssw_path_list = ssw_path_list if ssw_path_list is not None else []
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

    def _build_custom_scripts(self, scripts_and_args):
        """
        Generate custom IDL scripts from templates
        """
        scripts = []
        env = Environment(loader=FileSystemLoader([os.path.dirname(sa[0]) for sa in scripts_and_args
                                                   if os.path.isfile(sa[0])]))
        for sa in scripts_and_args:
            if os.path.isfile(sa[0]):
                scripts.append(env.get_template(os.path.basename(sa[0])).render(**sa[1]))
            else:
                scripts.append(env.from_string(sa[0]).render(**sa[1]))

        return scripts

    def _build_command_script(self, scripts, save_vars, save_filename, command_filename):
        """
        Generate parent IDL script
        """
        if save_vars is None:
            save_vars = []
        params = {'ssw_path_list': self.ssw_path_list, 'extra_paths': self.extra_paths, 'scripts': scripts,
                  'save_vars': save_vars, 'save_filename': save_filename}
        idl_commands = self.env.get_template('parent.pro').render(**params)
        with open(command_filename, 'w') as f:
            f.write(idl_commands)

    def _build_shell_script(self, command_filename, shell_filename):
        """
        Generate shell script for starting up SSWIDL
        """
        params = {'ssw_home': self.ssw_home, 'ssw_pkg_list': self.ssw_pkg_list,
                  'idl_home': self.idl_home, 'command_filename': command_filename}
        shell_script = self.env.get_template('startup.sh').render(**params)
        with open(shell_filename, 'w') as f:
            f.write(shell_script)

    def run(self, scripts_and_args, save_vars=None, cleanup=True, verbose=True):
        """
        Set up the SSWIDL environment and run the supplied scripts.

        Parameters
        ----------
        scripts_and_args : list
            List of tuples containing IDL scripts and arguments
        save_vars : list
            Variables to save and return from the IDL namespace
        cleanup : bool
            Delete temporary shell and .sav files
        verbose : bool
        """
        # generate filename for IDL sav file
        fn_template = os.path.join(self.hissw_home, '{name}_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.{ext}')
        save_filename = fn_template.format(name='idl_vars', ext='sav')
        command_filename = fn_template.format(name='idl_script', ext='pro')
        shell_filename = fn_template.format(name='ssw_shell', ext='sh')
        # generate custom scripts
        scripts = self._build_custom_scripts(scripts_and_args)
        # generate commands and save to file
        self._build_command_script(scripts, save_vars, save_filename, command_filename)
        # generate shell script
        self._build_shell_script(command_filename, shell_filename)
        # run the shell script
        subprocess.call(['chmod', 'u+x', shell_filename])
        try:
            cmd_output = subprocess.check_output(shell_filename, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            print(exc.output)
        else:
            if verbose: print(cmd_output.decode('utf-8'))
        # get results from save file
        results = readsav(save_filename)
        # delete scripts
        if cleanup:
            subprocess.call(['rm', command_filename])
            subprocess.call(['rm', shell_filename])
            subprocess.call(['rm', save_filename])

        return results
