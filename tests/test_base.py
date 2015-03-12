import os
import tempfile
import unittest
import shutil


test_links = {
            "direct": "https://i.imgur.com/AaLX1Wn.jpg",
            "imgur_link": "https://imgur.com/AaLX1Wn",
            "imgur_album": "https://imgur.com/a/IEKXq",
            "redditbooru_gallery": "http://awwnime.redditbooru.com/gallery/nchg/chiyo-chan/",
            "tumblr_link": "http://cowboy-bebop.tumblr.com/post/111839970633",
            }


class EnterTemp(unittest.TestCase):
    """Creates a temporary folder for each test.

    The current working directory will be set as this temporary folder.
    This folder will also have a subfolder named "sub".
    The folder will be cleaned up after each test.
    """
    def setUp(self):
        os.chdir(tempfile.mkdtemp())
        os.mkdir("sub")

    def tearDown(self):
        shutil.rmtree(os.getcwd(), ignore_errors=True)
