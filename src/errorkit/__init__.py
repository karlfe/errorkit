from importlib.metadata import PackageNotFoundError, version

from . import actions
from .models import ErrorDef
from .registry import ErrorRegistry, registry
from .severity import Severity

try:
    __version__ = version("errorkit")
except PackageNotFoundError:  # running from source without an install
    __version__ = "0.0.0+dev"

__all__ = ["Severity", "ErrorDef", "ErrorRegistry", "registry", "actions", "__version__"]
