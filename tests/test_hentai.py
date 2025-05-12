#!/usr/bin/env python3

import json
import sys
import unittest
from datetime import datetime as dt
from datetime import timezone
from random import choices
from urllib.parse import urlparse

from src.hentai import Hentai, Option, get_homepage


class TestHentai(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(571835)
        cls.test_response2 = Hentai(177014)

        read = lambda id: json.load(open(f"./tests/{id}.json", mode='r'))

        #cls.test_reference = Hentai(json=read(571835))
        cls.test_reference = cls.test_response

    @classmethod
    def tearDownClass(cls):
        pass

    def __test_image_urls(self, reference_url: str, response_url: str):
        reference_parsed = urlparse(reference_url)
        response_parsed = urlparse(response_url)

        self.assertEqual(reference_parsed.scheme, response_parsed.scheme, msg=str(self.test_response))
        self.assertEqual(reference_parsed.netloc[2:], response_parsed.netloc[2:], msg=str(self.test_response))
        self.assertEqual(reference_parsed.path, response_parsed.path, msg=str(self.test_response))

    def test_operators(self):
        self.assertFalse(self.test_response < self.test_response2)
        self.assertFalse(self.test_response <= self.test_response2)
        self.assertFalse(self.test_response == self.test_response2)
        self.assertTrue(self.test_response > self.test_response2)
        self.assertTrue(self.test_response >= self.test_response2)

    def test_init_exception(self):
        with self.assertRaises(TypeError) as context:
            Hentai(total=2)
        self.assertTrue('Insufficient arguments supplied to CTOR', context.exception)

    def test_repr(self):
        self.assertEqual(repr(self.test_response), f"Hentai(ID={self.test_response.id})", msg=repr(self.test_response))

    def test_response_json(self):
        self.assertNotIn('error', self.test_response.json, msg=str(self.test_response))

    def test_media_id(self):
        self.assertEqual(self.test_reference.media_id, self.test_response.media_id, msg=str(self.test_response))

    def test_title(self):
        self.assertEqual(self.test_reference.title(), self.test_response.title(), msg=str(self.test_response))

    def test_scanlator(self):
        self.assertEqual(self.test_reference.scanlator, self.test_response.scanlator, msg=str(self.test_response))

    def test_cover(self):
        self.__test_image_urls(self.test_reference.cover, self.test_response.cover)

    def test_thumbnail(self):
        self.__test_image_urls(self.test_reference.thumbnail, self.test_response.thumbnail)

    def test_upload_date(self):
        self.assertEqual(self.test_reference.upload_date, self.test_response.upload_date, msg=str(self.test_response))

    def test_tag(self):
        self.assertEqual(self.test_reference.tag, self.test_response.tag, msg=str(self.test_response))

    def test_group(self):
        self.assertEqual(self.test_reference.group, self.test_response.group, msg=str(self.test_response))

    def test_parody(self):
        self.assertEqual(self.test_reference.parody, self.test_response.parody, msg=str(self.test_response))

    def test_character(self):
        self.assertEqual(self.test_reference.character, self.test_response.character, msg=str(self.test_response))

    def test_language(self):
        self.assertEqual(self.test_reference.language, self.test_response.language, msg=str(self.test_response))

    def test_artist(self):
        self.assertEqual(self.test_reference.artist, self.test_response.artist, msg=str(self.test_response))

    def test_category(self):
        self.assertEqual(self.test_reference.category, self.test_response.category, msg=str(self.test_response))

    def test_related(self):
        self.assertEqual(len(self.test_response.related), 5, msg="Expected five related doujins as response.")

    def test_thread(self):
        first = self.test_response2.thread[-1]
        # comment
        self.assertEqual(first.id, 1006454, msg="Comment ID")
        self.assertEqual(first.gallery_id, self.test_response2.id, msg="Gallery ID")
        self.assertEqual(first.post_date, dt(2020, 6, 14, 19, 53, 27, tzinfo=timezone.utc), msg="Post Date")
        self.assertEqual(first.body, "Poor soul. It seems you are lost. The one you're looking for is only just a number behind. Take care. ", msg="Message")
        # poster
        self.assertEqual(first.poster.id, 1562493, msg="User ID")
        self.assertEqual(first.poster.username, "helogram", msg="User ID")
        self.assertEqual(first.poster.slug, "helogram", msg="User ID")
        self.__test_image_urls(first.poster.avatar_url, "https://i1.nhentai.net/avatars/1562493.png")
        #self.assertEqual(first.poster.avatar_url, "i.nhentai.net/avatars/1562493.png", msg="User ID")
        self.assertFalse(first.poster.is_superuser, msg="Super User Role")
        self.assertFalse(first.poster.is_staff, msg="Staff Member Role")

    def test_num_pages(self):
        self.assertEqual(self.test_reference.num_pages, self.test_response.num_pages, msg=str(self.test_response))

    def test_num_favorites(self):
        self.assertLessEqual(self.test_reference.num_favorites, self.test_response.num_favorites, msg=str(self.test_response))

    def test_num_favorites_edge_case(self):
        new_uploads = choices([*get_homepage().new_uploads], k=10)
        self.assertTrue(any(map(lambda doujin: doujin.num_favorites > 0, new_uploads)), msg=f"HTML parsing error sample {list(map(repr, new_uploads))}")

    def test_image_urls(self):
        for image_url in map(urlparse, choices(self.test_response.image_urls, k=10)):
            self.assertTrue(image_url.scheme, msg=f"AssertSchemeError: {image_url}")
            self.assertTrue(image_url.netloc, msg=f"AssertNetlocError: {image_url}")
            self.assertTrue(image_url.path, msg=f"AssertPathError: {image_url}")

    def test_exists(self):
        self.assertTrue(Hentai.exists(self.test_response.id), msg=str(self.test_response))
        self.assertFalse(Hentai.exists(sys.maxsize), msg=f"Should have failed:{sys.maxsize}")
        self.assertFalse(Hentai.exists(-69), msg=f"Should have failed:{-69}")

    def test_dictionary_exception(self):
        with self.assertRaises(NotImplementedError) as context:
            self.test_response.dictionary([Option.Raw])
        self.assertTrue('Category Exception is not implemented', context.exception)

if __name__ == '__main__':
    unittest.main()
