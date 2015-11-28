import os
import unittest
from unittest import mock
from tests import test_base
from redditcurl import websites


test_links = test_base.test_links


class TestMatcher(unittest.TestCase):
    def test_direct(self):
        self.assertTrue(websites.direct.match(test_links["direct"]))

    def test_gfycat(self):
        self.assertTrue(websites.gfycat.match(test_links["gfycat"]))
        
    def test_imgur_link(self):
        self.assertTrue(websites.imgur_link.match(test_links["imgur_link"]))

    def test_imgur_album(self):
        self.assertTrue(websites.imgur_album.match(test_links["imgur_album"]))

    def test_imgur_gifv(self):
        self.assertTrue(websites.imgur_gifv.match(test_links["imgur_gifv"]))
        
    def test_redditbooru_gallery(self):
        self.assertTrue(websites.redditbooru_gallery.match(test_links["redditbooru_gallery"]))

    def test_deviantart(self):
        self.assertTrue(websites.deviantart.match(test_links["deviantart"]))

    def test_fail(self):
        self.assertFalse(websites.direct.match(test_links["fail"]))
        self.assertFalse(websites.imgur_link.match(test_links["fail"]))
        self.assertFalse(websites.imgur_album.match(test_links["fail"]))
        self.assertFalse(websites.redditbooru_gallery.match(test_links["fail"]))


class TestDownloadNamed(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "", "direct")
        self.assertTrue(os.path.isfile("direct.jpeg"))

    def test_gfycat(self):
        websites.gfycat.download(test_links["gfycat"], "", "Penguin in snow")
        self.assertTrue(os.path.isfile("Penguin in snow.webm"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "", "Emperor Penguin")
        self.assertTrue(os.path.isfile("Emperor Penguin.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "", "penguins")
        self.assertTrue(os.path.isfile("penguins.1.jpg"))
        self.assertTrue(os.path.isfile("penguins.2.jpg"))
        self.assertTrue(os.path.isfile("penguins.3.jpg"))

    def test_imgur_gifv(self):
        websites.imgur_gifv.download(test_links["imgur_gifv"], "", "walking penguin")
        self.assertTrue(os.path.isfile("walking penguin.webm"))

    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "anime")
        self.assertTrue(os.path.isfile("anime.1.jpeg"))
        self.assertTrue(os.path.isfile("anime.2.jpeg"))
        self.assertTrue(os.path.isfile("anime.3.jpeg"))

    def test_deviantart(self):
        websites.deviantart.download(test_links["deviantart"], "", "oblivion")
        self.assertTrue(os.path.isfile("oblivion.jpeg"))


class TestDownloadUnnamed(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_gfycat(self):
        websites.gfycat.download(test_links["gfycat"], "", "")
        self.assertTrue(os.path.isfile("QualifiedDefensiveAddax.webm"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "", "")
        self.assertTrue(os.path.isfile("AaLX1Wn.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "", "")
        self.assertTrue(os.path.isfile("1 - AaLX1Wn.jpg"))
        self.assertTrue(os.path.isfile("2 - ASXSZ2e.jpg"))
        self.assertTrue(os.path.isfile("3 - 3TaDvRX.jpg"))

    def test_imgur_gifv(self):
        websites.imgur_gifv.download(test_links["imgur_gifv"], "", "")
        self.assertTrue(os.path.isfile("bJ0h81c.webm"))

    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "", "")
        self.assertTrue(os.path.isfile("o961.jpeg"))
        self.assertTrue(os.path.isfile("o962.jpeg"))
        self.assertTrue(os.path.isfile("o963.jpeg"))

    def test_deviantart(self):
        websites.deviantart.download(test_links["deviantart"], "", "")
        self.assertTrue(os.path.isfile("oblivion_of_mehrunes_by_magusverus.jpeg"))


class TestDownloadPath(test_base.EnterTemp):
    def test_direct(self):
        websites.direct.download(test_links["direct"], "sub", "direct")
        self.assertTrue(os.path.isfile("sub/direct.jpeg"))

    def test_gfycat(self):
        websites.gfycat.download(test_links["gfycat"], "sub", "Penguin in snow")
        self.assertTrue(os.path.isfile("sub/Penguin in snow.webm"))

    def test_imgur_link(self):
        websites.imgur_link.download(test_links["imgur_link"], "sub", "Emperor Penguin")
        self.assertTrue(os.path.isfile("sub/Emperor Penguin.jpeg"))

    def test_imgur_album(self):
        websites.imgur_album.download(test_links["imgur_album"], "sub", "penguins")
        self.assertTrue(os.path.isfile("sub/penguins.1.jpg"))
        self.assertTrue(os.path.isfile("sub/penguins.2.jpg"))
        self.assertTrue(os.path.isfile("sub/penguins.3.jpg"))

    def test_imgur_gifv(self):
        websites.imgur_gifv.download(test_links["imgur_gifv"], "sub", "walking penguin")
        self.assertTrue(os.path.isfile("sub/walking penguin.webm"))
                        
    def test_redditbooru_gallery(self):
        websites.redditbooru_gallery.download(test_links["redditbooru_gallery"], "sub", "anime")
        self.assertTrue(os.path.isfile("sub/anime.1.jpeg"))
        self.assertTrue(os.path.isfile("sub/anime.2.jpeg"))
        self.assertTrue(os.path.isfile("sub/anime.3.jpeg"))

    def test_deviantart(self):
        websites.deviantart.download(test_links["deviantart"], "sub", "oblivion")
        self.assertTrue(os.path.isfile("sub/oblivion.jpeg"))


class TestSharedConfig(test_base.EnterTemp):
    """Test the alternative configurations for the downloaders."""

    @mock.patch("redditcurl.websites.shared_config.PREFER_MP4", new=True)
    def test_gfycat_mp4(self):
        websites.gfycat.download(test_links["gfycat"], "", "Penguin in snow")
        self.assertTrue(os.path.isfile("Penguin in snow.mp4"))


    @mock.patch("redditcurl.websites.shared_config.PREFER_MP4", new=True)
    def test_imgur_gifv_mp4(self):
        websites.imgur_gifv.download(test_links["imgur_gifv"], "", "walking penguin")
        self.assertTrue(os.path.isfile("walking penguin.mp4"))
