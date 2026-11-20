import logging

__all__ = ['_init_log']


def _init_log():
    """
    Initializes the fiasco log.

    In most circumstances this is called automatically when importing
    fiasco. This code is based on that provided by Astropy see
    "licenses/ASTROPY.rst".
    """
    orig_logger_cls = logging.getLoggerClass()
    log = logging.getLogger('hissw')
    logging.setLoggerClass(orig_logger_cls)

    return log
