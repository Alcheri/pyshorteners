# coding: utf-8
import unittest

from pyshorteners import Shortener

class ShortenersTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://www.google.com'
        self.module = __import__('pyshorteners.shorteners')

    def test_shorteners_type(self):
        shorteners = ['GoogleShortener', 'BitlyShortener', 'TinyurlShortener']
        for shortener in shorteners:
            short = Shortener(shortener)
            self.assertEqual(type(short), short.__class__)


    def test_googl_short_function(self):
        engine = 'GoogleShortener'
        short = Shortener(engine)
        self.assertEqual(short.short('http://www.google.com'),
                         'http://goo.gl/fbsS')


    def test_googl_expand_function(self):
        engine = 'GoogleShortener'
        short = Shortener(engine)
        self.assertEqual(short.expand('http://goo.gl/fbsS'),
                         'http://www.google.com/')


    def test_tinyurl_short_function(self):
        engine = 'TinyurlShortener'
        short = Shortener(engine)
        self.assertEqual(short.short('http://www.google.com'),
                         'http://tinyurl.com/1c2')


    def test_tinyurl_expand_function(self):
        engine = 'TinyurlShortener'
        short = Shortener(engine)
        self.assertEqual(short.expand('http://tinyurl.com/ycus76'),
                         u'https://www.facebook.com')


    def test_wrong_shortener_engine(self):
        engine = 'UnknownShortener'
        with self.assertRaises(AttributeError):
            Shortener(engine)


if __name__ == '__main__':
    unittest.main()
