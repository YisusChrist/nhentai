#!/usr/bin/env python3

import unittest
from urllib.parse import urljoin

from src.hentai import Hentai, Option, Tag
from src.hentai.consts import HOME_URL


class TestTag(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_response = Hentai(177014)

    def test_get(self):
        self.assertEqual(Tag.get(self.test_response.language, 'name'), "translated, chinese", msg=f"Language Tag: {self.test_response.language}")

    def test_get_exception(self):
        with self.assertRaises(ValueError) as context:
            Tag.get(self.test_response.language, 'upload_date')
        self.assertTrue('DNE', context.exception)

    def test_list(self):
        characters = Tag.list(Option.Character, local_=True)
        for character in characters:
            if character.name == 'holo':
                self.assertEqual(character.id, 33918)
                self.assertEqual(character.type, 'character')
                self.assertEqual(character.name, 'holo')
                self.assertEqual(character.url, urljoin(HOME_URL, '/character/holo/'))
                self.assertEqual(character.count, 160)
                break

    def test_list_first_exception(self):
        with self.assertRaises(ValueError) as context:
            Tag.list(Option.Epos)
        self.assertTrue('Epos Option is not supported', context.exception)

    def test_list_second_exception(self):
        with self.assertRaises(NotImplementedError) as context:
            Tag.list(Option.Category)
        self.assertTrue('Category Exception is not implemented', context.exception)

    def test_empty_search(self):
        artist = "nonexistentartist"
        result = Tag.search(Option.Artist, 'name', artist, local_=True)
        self.assertIsNone(result, msg=f"Search should return None for '{artist}' artist")

    def test_search(self):
        result = Tag.search(Option.Artist, 'name', 'katase minami', local_=True)
        artist = self.test_response.artist[0]
        self.assertEqual(artist.id, result.id, msg="IDs should be an exact match")
        self.assertEqual(artist.type, result.type, msg="Types should be an exact match")
        self.assertEqual(artist.name, result.name, msg="Names should be an exact match")
        self.assertEqual(artist.url, result.url, msg="URLs should be an exact match")
        self.assertAlmostEqual(artist.count, result.count, delta=100, msg="Count should be almost equal")
