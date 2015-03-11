import os
import tempfile
import unittest
import shutil
from redditcurl import websites


test_links = {
            "direct": "https://i.imgur.com/AaLX1Wn.jpg",
            "imgur_link": "https://imgur.com/AaLX1Wn",
            "imgur_album": "https://imgur.com/a/IEKXq",
            "redditbooru_gallery": "http://awwnime.redditbooru.com/gallery/nchg/chiyo-chan/",
            "tumblr_link": "http://cowboy-bebop.tumblr.com/post/111839970633",
            }


class TestDownload(unittest.TestCase):
    def setUp(self):
        os.chdir(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(os.getcwd(), ignore_errors=True)

    def test_direct(self):
        self.assertTrue(websites.direct.match(test_links["direct"]))
        websites.direct.download(test_links["direct"], "", "direct")
        self.assertTrue(os.path.isfile("direct.jpeg"))
        websites.direct.download(test_links["direct"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_imgur_link(self):
        self.assertTrue(websites.imgur_link.match(test_links["imgur_link"]))
        websites.imgur_link.download(test_links["imgur_link"], "", "Emperor Penguin")
        self.assertTrue(os.path.isfile("Emperor Penguin.jpeg"))
        websites.imgur_link.download(test_links["imgur_link"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_imgur_album(self):
        self.assertTrue(websites.imgur_album.match(test_links["imgur_album"]))
        websites.imgur_album.download(test_links["imgur_album"], "", "penguins")
        self.assertTrue(os.path.isfile("penguins.1.jpg"))
        self.assertTrue(os.path.isfile("penguins.2.jpg"))
        self.assertTrue(os.path.isfile("penguins.3.jpg"))
        websites.imgur_album.download(test_links["imgur_album"], "", "")
        self.assertTrue(os.path.isfile("1 - AaLX1Wn.jpg"))
        self.assertTrue(os.path.isfile("2 - ASXSZ2e.jpg"))
        self.assertTrue(os.path.isfile("3 - 3TaDvRX.jpg"))

    def test_redditbooru_gallery(self):
        self.assertTrue(websites.redditbooru_gallery.match(test_links["redditbooru_gallery"]))
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "anime")
        self.assertTrue(os.path.isfile("anime.1.jpeg"))
        self.assertTrue(os.path.isfile("anime.2.jpeg"))
        self.assertTrue(os.path.isfile("anime.3.jpeg"))
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "")
        self.assertTrue(os.path.isfile("o961.jpeg"))
        self.assertTrue(os.path.isfile("o962.jpeg"))
        self.assertTrue(os.path.isfile("o963.jpeg"))

    def test_tumblr_link(self):
        self.assertTrue(websites.tumblr_link.match(test_links["tumblr_link"]))
        websites.tumblr_link.download(test_links["tumblr_link"], "", "bebop")
        self.assertTrue(os.path.isfile("bebop.jpeg"))
        websites.tumblr_link.download(test_links["tumblr_link"], "", "")
        self.assertTrue(os.path.isfile("tumblr_niwgy0oXdq1tv7a6ao1_500.jpeg"))
