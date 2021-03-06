# ===========================================================================
#   __init__.py -------------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import logging
import os

#   settings ----------------------------------------------------------------
# ---------------------------------------------------------------------------
__license__ = "MIT"
__version__ = '0.4.2'
__author__ = __maintainer__ = "Wolfgang Brandenburger"
__email__ = "wolfgang.brandenburger@outlook.com"

#   script ------------------------------------------------------------------
# ---------------------------------------------------------------------------
try:
    import colorama
    colorama.init()

    if os.environ.get("RSVIS_DEBUG"):
        log_format = (
            'File "%(pathname)s", line %(lineno)s:\n' +
            colorama.Fore.YELLOW +
            '%(levelname)s' +
            ':' +
            colorama.Fore.GREEN +
            '%(name)s' +
            colorama.Fore.CYAN +
            ':' +
            '%(message)s' +
            colorama.Style.RESET_ALL
        )
    else:        
        log_format = (
            colorama.Fore.YELLOW +
            '%(levelname)s' +
            ':' +
            colorama.Fore.GREEN +
            '%(name)s' +
            colorama.Fore.CYAN +
            ':' +
            '%(message)s' +
            colorama.Style.RESET_ALL
        )
          
    logging.basicConfig(format=log_format)
    _logger = logging.getLogger("rsvis")

    if os.environ.get("RSVIS_DEBUG"):
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)

except ImportError:
    pass
