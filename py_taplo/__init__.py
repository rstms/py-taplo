"""python wrapper for taplo"""

# https://taplo.tamasfe.dev/

from .cli import cli
from .taplo import Taplo
from .version import __author__, __email__, __timestamp__, __version__

__all__ = [
    "Taplo",
    "cli",
    "__version__",
    "__timestamp__",
    "__author__",
    "__email__",
]
