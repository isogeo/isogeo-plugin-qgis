# -*- coding: utf-8 -*-

# Standard library
import unittest
import json

# Tested module
from modules import ApiRequester

class TestApiRequester(unittest.TestCase):

    def setUp(self):
        self.requester = ApiRequester()
    
    def tearDown(self):
        pass
     
    def test_setup_api_params(self):
        pass

    def test_create_request(self):
        pass

    def test_send_request(self):
        pass

    def test_handle_request(self):
        pass
    
    def test_build_request_url(self):
        pass


if __name__ == '__main__':
    unittest.main()