# coding: utf-8

from django.utils import unittest

from models import Color

class ColorTestCase(unittest.TestCase):
    def setUp(self):
        self.color_value = '#00ffbb'

    def test_add(self):
        Color.add(self.color_value)
        color = Color.objects.get(value=self.color_value)
        self.assertNotEqual(color, None)

    def test_get(self):
        color = Color.get(self.color_value)
        self.assertNotEqual(color, None)

    def test_like_users(self):
        color = Color.get(self.color_value)
        self.assertEqual(len(list(color.like_users())), 0)

    def test_tags(self):
        color = Color.get(self.color_value)
        self.assertEqual(color.tags().count(), 0)

class UserTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_add_user(self):
        pass
