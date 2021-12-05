"""xautic: live reloading with Python."""

from .main import StatReloader
from .main import debug
from .main import restart_with_reloader
from .main import run_with_reloader

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

__all__ = [
    "__version__",
    "StatReloader",
    "debug",
    "restart_with_reloader",
    "run_with_reloader",
]
