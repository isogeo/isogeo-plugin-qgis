# -*- coding: utf-8 -*-

# Standard library
import unittest
import json
import os
from pathlib import Path

# PyQT
from qgis.PyQt.QtCore import QSettings


# Tested module
from modules import Authenticator


class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        auth_folder = Path(__file__).parents[0] / "_auth"
        self.authenticator = Authenticator()
        self.authenticator.lang = "fr"
        self.qsettings = QSettings

    def tearDown(self):
        pass

    def test_instantiation(self):
        with self.assertRaises(TypeError):
            Authenticator(1)
        with self.assertRaises(ValueError):
            Authenticator()
        self.assertEqual(Authenticator("path").auth_folder, "path")

    def test_credentials_check_qsettings(self):
        self.qsettings.beginGroup("isogeo-plugin")
        self.qsettings.close()
        self.assertFalse(self.authenticator.credentials_check_qsettings())

    def test_credentials_check_file(self):
        os.rename(
            Path(self.authenticator.auth_folder) / "client_secrets.json",
            Path(self.authenticator.auth_folder) / "client_secrets_test.json",
        )
        self.assertFalse(self.authenticator.credentials_check_file())
        os.rename(
            Path(self.authenticator.auth_folder) / "client_secrets_test.json",
            Path(self.authenticator.auth_folder) / "client_secrets.json",
        )

    def test_credentials_update(self):
        pass

    def test_credentials_storer(self):
        pass

    def test_credentials_uploader(self):
        pass

    def test_manage_api_initialization(self):
        pass


if __name__ == "__main__":
    unittest.main()
