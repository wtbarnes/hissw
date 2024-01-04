"""
Any utility functions
"""

__all__ = ['SSWIDLError', 'IDLLicenseError']


class SSWIDLError(Exception):
    """
    An error to raise when something goes wrong in SSW
    """
    pass


class SSWNotFoundError(Exception):
    """
    An error to raise when an SSW installation cannot be found
    """
    pass


class IDLLicenseError(Exception):
    """
    An error to raise when IDL cannot find a license
    """
    pass


class IDLNotFoundError(Exception):
    """
    An error to raise when an IDL installation cannot be found
    """
    pass
