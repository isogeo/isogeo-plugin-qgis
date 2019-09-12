# -*- coding: utf-8 -*-

# Standard library
import unittest
import json
import os
from pathlib import Path

# Tested module
from modules import CacheManager


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache_file = Path(__file__).parents[0] / "cache_test.json"
        self.cache_mng = CacheManager(str(self.cache_file))

    def test_instantiation(self):
        with self.assertRaises(TypeError):
            CacheManager(1)
        with self.assertRaises(ValueError):
            CacheManager()
        self.assertEqual(CacheManager("path").cache_file, "path")

    def test_properties(self):
        self.assertTrue(isinstance(self.cache_mng.cached_dict, dict))
        self.assertTrue(isinstance(self.cache_mng.cached_unreach_paths, list))
        self.assertTrue(isinstance(self.cache_mng.cached_unreach_postgis, list))
        self.assertTrue(isinstance(self.cache_mng.cached_unreach_srv, list))

    def test_dumper(self):
        self.cache_mng.cached_unreach_paths = ["path1", "path2", "path1"]
        self.cache_mng.cached_unreach_postgis = ["pg3", "pg4", "pg5", "pg3"]
        self.cache_mng.cached_unreach_srv = ["srv6"]

        self.assertTrue(isinstance(self.cache_mng.dumper(), dict))
        self.assertEqual(self.cache_mng.dumper().get("services"), ["srv6"])

    def test_loader(self):
        self.assertTrue(isinstance(self.cache_mng.loader(), list))
        self.assertTrue(isinstance(self.cache_mng.loader()[0], dict))

        self.assertTrue(isinstance(self.cache_mng.cached_unreach_paths, list))
        self.assertTrue(isinstance(self.cache_mng.cached_unreach_postgis, list))
        self.assertTrue(isinstance(self.cache_mng.cached_unreach_srv, list))

        self.assertEqual(
            sorted(self.cache_mng.cached_unreach_paths), sorted(["path1", "path2"])
        )
        self.assertEqual(
            sorted(self.cache_mng.cached_unreach_postgis), sorted(["pg3", "pg4", "pg5"])
        )
        self.assertEqual(self.cache_mng.cached_unreach_srv, ["srv6"])

    def test_loader_old_files(self):
        with open(self.cache_mng.cache_file, "w") as cache:
            json.dump(["old/path"], cache, indent=4)

        self.assertTrue(isinstance(self.cache_mng.loader(), list))
        self.assertTrue(isinstance(self.cache_mng.loader()[0], str))
        self.assertEqual(self.cache_mng.loader()[0], "old/path")
        self.assertEqual(self.cache_mng.cached_unreach_paths, ["old/path"])

    def test_cleaner(self):
        self.cache_mng.cleaner()

        self.assertEqual(self.cache_mng.cached_unreach_paths, [])
        self.assertEqual(self.cache_mng.cached_unreach_postgis, [])
        self.assertEqual(self.cache_mng.cached_unreach_srv, [])


if __name__ == "__main__":
    unittest.main()
