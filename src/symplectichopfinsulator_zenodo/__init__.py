"""Path management and HDF5 helpers, vendored from PyWatson
(https://github.com/isaac-tes/pywatson) for this repo's figure scripts.
"""

from .pywatson_utils import datadir, plotsdir, load_data

__version__ = "1.0.0"
__author__ = "Isaac Tesfaye"
__email__ = "i.tesfaye@tu-berlin.de"

__all__ = ["datadir", "plotsdir", "load_data"]
