"""
Define some useful Jinja2 filters
"""
import numpy as np

__all__ = ['units_filter',
           'log10_filter',
           'string_list_filter',
           'force_double_precision_filter',]


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


def force_double_precision_filter(value):
    """
    Force a number (or array of numbers) to have double precision in IDL.

    hissw relies on string representations of Python objects when inserting
    values into the resulting IDL script. However, the default string representation
    of Python floats is truncated well below the actual floating point precision.
    See https://docs.python.org/3/tutorial/floatingpoint.html#floating-point-arithmetic-issues-and-limitations.
    Thus, to preserve precision, this filter uses the `as_integer_ratio` method
    to represent floating point values as division operations between integer values
    to ensure that precision is preserved when passing floating point values from
    IDL into Python. When used in combination with other filters, this filter should
    be used last as it forces a conversion to a list of strings.
    """
    if isinstance(value, (np.ndarray, list)):
        str_list = [force_double_precision_filter(x) for x in value]
        # NOTE: this has to be done manually because each entry is formatted as a
        # string such that the division is not evaluated in Python. However, we
        # want this to be inserted as an array of integer divison operations.
        return f"[{','.join(str_list)}]"
    else:
        # If it is neither an array or list, 
        a, b = value.as_integer_ratio()
        return f'{a}d / {b}d'