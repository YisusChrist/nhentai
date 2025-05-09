#!/usr/bin/env python3

import unittest

from src.hentai import Hentai


class TestPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(571835)
        cls.cover = cls.test_response.pages[0]

    @classmethod
    def tearDownClass(cls):
        cls.cover.filename.unlink()

    def test_filename(self):
        self.assertEqual('1.webp', str(self.cover.filename), msg=f"Wrong filename: {self.cover.filename!r}")

    def test_download(self):
        self.cover.download(self.test_response.handler)
        self.assertTrue(self.cover.filename.exists(), msg=f"Download failed: {self.cover.filename!r}")
