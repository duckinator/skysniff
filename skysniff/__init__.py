#!/usr/bin/env python3

from .nws import NWSApi

# Expose `skysniff.version.__version__` as `skysniff.__version__`.
from .version import __version__

__all__ = [
    "NWSApi",
    "__version__",
]
