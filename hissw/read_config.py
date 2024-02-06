"""
Read some default options if possible
"""

import os
import pathlib
import configparser

HISSW_DIR = pathlib.Path.home() / '.hissw'
HISSW_RC = HISSW_DIR / 'hisswrc'


defaults = {}
defaults['hissw_home'] = HISSW_DIR
if HISSW_RC.is_file():
    config = configparser.ConfigParser()
    config.read(HISSW_RC)
    for key in config['hissw']:
        defaults[key] = config['hissw'][key]
else:
    defaults['ssw_home'] = None
    defaults['idl_home'] = None
