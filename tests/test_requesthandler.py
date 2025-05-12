#!/usr/bin/env python3

import unittest
from urllib.parse import urljoin

from hentai.consts import HOME_URL
from src.hentai.requests import RequestHandler


class TestRequestHandler(unittest.TestCase):
    def test_call_api(self):
        url: str = urljoin(HOME_URL, "api/galleries/all")
        response = RequestHandler().get(url)
        self.assertTrue(response.ok)
        self.assertNotIn('error', response.json())


if __name__ == '__main__':
    unittest.main()
