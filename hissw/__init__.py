'''
hissw -- integrate SSW into Python workflows
'''
from .environment import Environment
from .logger import _init_log
from .read_config import defaults
from .util import (IDLLicenseError, IDLNotFoundError, SSWIDLError,
                   SSWNotFoundError)

log = _init_log()
