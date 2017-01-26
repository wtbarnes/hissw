'''
Build SSW scripts from Jinja 2 templates
'''
import os
import datetime
import subprocess

from jinja2 import Environment,Template,FileSystemLoader
from scipy.io import readsav

from .read_config import defaults

class ScriptMaker(object):
    """
    Build and execute SSW IDL scripts
    """

    def __init__(self,ssw_pkg_list=[], ssw_path_list=[], ssw_home=None, idl_home=None, hissw_home=None, extra_paths=[]):
        self.ssw_pkg_list = ssw_pkg_list
        self.ssw_path_list = ssw_path_list
        self.extra_paths = extra_paths
        self.env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))
        if ssw_home is None:
            if defaults['ssw_home'] is None:
                raise ValueError('''ssw_home must be set at instantiation or
                                    in the hisswrc file.''')
            else:
                self.ssw_home = defaults['ssw_home']
        else:
            self.ssw_home = ssw_home
        if idl_home is None:
            if defaults['idl_home'] is None:
                raise ValueError('''idl_home must be set at instantiation or
                                    in the hisswrc file.''')
            else:
                self.idl_home = defaults['idl_home']
        else:
            self.idl_home = idl_home
        if hissw_home is None:
            if defaults['hissw_home'] is None:
                raise ValueError('''hissw_home must be set at instantiation or
                                    in the hisswrc file.''')
            else:
                self.hissw_home = defaults['hissw_home']
        else:
            self.hissw_home = hissw_home

    def _build_custom_scripts(self,scripts_and_args):
        """Generate user scripts from templates"""
        scripts = []
        env = Environment(
            loader=FileSystemLoader([os.path.dirname(sa[0]) for sa in scripts_and_args]))
        for sa in scripts_and_args:
            scripts.append(env.get_template(os.path.basename(sa[0])).render(**sa[1]))

        return scripts

    def _build_command_script(self,scripts,save_vars,save_filename,command_filename):
        """Generate command script and save to file"""
        idl_commands = self.env.get_template('parent.com').render(
                                        ssw_path_list=self.ssw_path_list,
                                        extra_paths=self.extra_paths,
                                        scripts=scripts,
                                        save_vars=save_vars,
                                        save_filename=save_filename)
        with open(command_filename,'w') as f:
            f.write(idl_commands)

    def _build_shell_script(self,command_filename,shell_filename):
        """Generate shell script"""
        shell_script = self.env.get_template('startup.sh').render(
                                ssw_home=self.ssw_home,
                                idl_home=self.idl_home,
                                ssw_pkg_list=self.ssw_pkg_list,
                                command_filename=command_filename)
        with open(shell_filename,'w') as f:
            f.write(shell_script)

    def run(self,scripts_and_args,save_vars=[]):
        """
        Generate shell script, run it, and return dictionary with variables
        from IDL session
        """
        #generate filename for IDL sav file
        fn_template = os.path.join(self.hissw_home,
                    '{name}_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.{ext}')
        save_filename = fn_template.format(name='idl_vars',ext='sav')
        command_filename = fn_template.format(name='idl_script',ext='com')
        shell_filename = fn_template.format(name='ssw_shell',ext='sh')
        #generate custom scripts
        scripts = self._build_custom_scripts(scripts_and_args)
        #generate commands and save to file
        self._build_command_script(scripts,save_vars,save_filename,command_filename)
        #generate shell script
        self._build_shell_script(command_filename,shell_filename)
        #run the shell script
        subprocess.call(['chmod','u+x',shell_filename])
        subprocess.check_output(shell_filename,shell=True)

        return readsav(save_filename)
