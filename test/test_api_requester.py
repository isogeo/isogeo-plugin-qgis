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

    def test_api_auth_post_get_token(self):
        pass

    def test_api_auth_handle_token(self):
        pass

    def test_api_get_requests(self):
        pass

    def test_api_requests_handle_reply(self):
        pass
    
    def test_build_request_url(self):
        pass


if __name__ == '__main__':
    unittest.main()