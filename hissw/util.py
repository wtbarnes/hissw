"""
Any utility functions
"""

__all__ = ['SSWIDLError', 'IDLLicenseError']


class SSWIDLError(Exception):
    """
    An error to raise when something goes wrong in SSW
    """
    pass


class IDLLicenseError(Exception):
    """
    An error to raise when IDL cannot find a license
    """
    pass
