"""
Read some default options if possible
"""

import os
import configparser


defaults = {}
defaults['hissw_home'] = os.path.join(os.environ['HOME'], '.hissw')
if os.path.isfile(os.path.join(os.environ['HOME'], '.hissw', 'hisswrc')):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.environ['HOME'], '.hissw', 'hisswrc'))
    for key in config['hissw']:
        defaults[key] = config['hissw'][key]
else:
    defaults['ssw_home'] = None
    defaults['idl_home'] = None
