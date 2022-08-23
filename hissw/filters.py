"""
Define some useful Jinja2 filters
"""
import numpy as np

__all__ = ['units_filter', 'log10_filter']


def units_filter(quantity, unit):
    """
    Convert quantity to given units and extract value.
    """
    import astropy.units as u  # Avoid astropy as a hard dependency
    if not isinstance(quantity, u.Quantity):
        raise u.UnitsError(f'Value must be a quantity with units compatible with {unit}')
    return quantity.to_value(unit)


def log10_filter(value):
    """
    Take the base 10 log of a given value.
    """
    return np.log10(value)


def string_list_filter(string_list):
    """
    Double quote a list of strings.
    
    This is needed when passing in a list of strings to IDL as each string
    in the list will not be quoted when passed into the template.
    """
    return [f"'{s}'" for s in string_list]
