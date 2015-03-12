import os
import unittest
from tests import test_base
from redditcurl import websites


test_links = test_base.test_links


class TestMatcher(unittest.TestCase):
    def test_direct(self):
        self.assertTrue(websites.direct.match(test_links["direct"]))

    def test_imgur_link(self):
        self.assertTrue(websites.imgur_link.match(test_links["imgur_link"]))

    def test_imgur_album(self):
        self.assertTrue(websites.imgur_album.match(test_links["imgur_album"]))

    def test_redditbooru_gallery(self):
        self.assertTrue(websites.redditbooru_gallery.match(test_links["redditbooru_gallery"]))

    def test_tumblr_link(self):
        self.assertTrue(websites.tumblr_link.match(test_links["tumblr_link"]))


class TestDownloadNamed(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "", "direct")
        self.assertTrue(os.path.isfile("direct.jpeg"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "", "Emperor Penguin")
        self.assertTrue(os.path.isfile("Emperor Penguin.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "", "penguins")
        self.assertTrue(os.path.isfile("penguins.1.jpg"))
        self.assertTrue(os.path.isfile("penguins.2.jpg"))
        self.assertTrue(os.path.isfile("penguins.3.jpg"))

    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "anime")
        self.assertTrue(os.path.isfile("anime.1.jpeg"))
        self.assertTrue(os.path.isfile("anime.2.jpeg"))
        self.assertTrue(os.path.isfile("anime.3.jpeg"))

    def test_tumblr_link(self):
        websites.tumblr_link.download(test_links["tumblr_link"], "", "bebop")
        self.assertTrue(os.path.isfile("bebop.jpeg"))


class TestDownloadUnnamed(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "", "")
        self.assertTrue(os.path.isfile("1 - AaLX1Wn.jpg"))
        self.assertTrue(os.path.isfile("2 - ASXSZ2e.jpg"))
        self.assertTrue(os.path.isfile("3 - 3TaDvRX.jpg"))

    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "")
        self.assertTrue(os.path.isfile("o961.jpeg"))
        self.assertTrue(os.path.isfile("o962.jpeg"))
        self.assertTrue(os.path.isfile("o963.jpeg"))

    def test_tumblr_link(self):
        websites.tumblr_link.download(test_links["tumblr_link"], "", "")
        self.assertTrue(os.path.isfile("tumblr_niwgy0oXdq1tv7a6ao1_500.jpeg"))


class TestDownloadPath(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "sub", "direct")
        self.assertTrue(os.path.isfile("sub/direct.jpeg"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "sub", "Emperor Penguin")
        self.assertTrue(os.path.isfile("sub/Emperor Penguin.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "sub", "penguins")
        self.assertTrue(os.path.isfile("sub/penguins.1.jpg"))
        self.assertTrue(os.path.isfile("sub/penguins.2.jpg"))
        self.assertTrue(os.path.isfile("sub/penguins.3.jpg"))

    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "sub", "anime")
        self.assertTrue(os.path.isfile("sub/anime.1.jpeg"))
        self.assertTrue(os.path.isfile("sub/anime.2.jpeg"))
        self.assertTrue(os.path.isfile("sub/anime.3.jpeg"))

    def test_tumblr_link(self):
        websites.tumblr_link.download(test_links["tumblr_link"], "sub", "bebop")
        self.assertTrue(os.path.isfile("sub/bebop.jpeg"))
