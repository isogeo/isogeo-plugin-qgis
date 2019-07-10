# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'projets+qgis@isogeo.fr'
__date__ = '2019-07-10'
__copyright__ = 'Copyright 2016, Isogeo, Simon Sampere, GeoJulien'
import unittest
import os

from qgis.PyQt.QtGui import QIcon


class IsogeoResourcesTest(unittest.TestCase):
    """Test resources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test plugin icon file validity."""
        basepath = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(basepath, "icon.png")
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(IsogeoResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


