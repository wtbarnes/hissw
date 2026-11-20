"""
Read some default options if possible
"""
import configparser
import pathlib

HISSW_DIR = pathlib.Path.home() / '.hissw'
HISSW_RC = HISSW_DIR / 'hisswrc'


defaults = {'hissw_home': HISSW_DIR, 'ssw_home': None, 'idl_home': None}
config = configparser.ConfigParser()
config.read(HISSW_RC)  # a missing file is skipped
if config.has_section('hissw'):
    defaults.update(config['hissw'])
