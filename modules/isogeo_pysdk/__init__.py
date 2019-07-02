#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This module is an abstraction calls about the Isogeo REST API.
    https://www.isogeo.com/
"""

from .isogeo_sdk import Isogeo, version
from .checker import IsogeoChecker
from .translator import IsogeoTranslator
from .utils import IsogeoUtils

__version__ = version
VERSION = __version__
