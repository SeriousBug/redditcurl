import os
import tempfile
import unittest
import shutil
from unittest.mock import MagicMock


test_links = {
    "direct": "https://i.imgur.com/AaLX1Wn.jpg",
    "gfycat": "https://gfycat.com/QualifiedDefensiveAddax",
    "imgur_link": "https://imgur.com/AaLX1Wn",
    "imgur_album": "https://imgur.com/a/IEKXq",
    "imgur_gifv": "https://i.imgur.com/bJ0h81c.gifv",
    "redditbooru_gallery": "http://awwnime.redditbooru.com/gallery/nchg/chiyo-chan/",
    "tumblr_link": "http://cowboy-bebop.tumblr.com/post/111839970633",
    "fail": "https://github.com/SeriousBug/redditcurl"
    }

test_links_404 = {
    "direct": "https://i.imgur.com/000000.jpg",
    "gfycat": "https://gfycat.com/00000000000000",
    "imgur_link": "https://imgur.com/000000000",
    "imgur_album": "https://imgur.com/a/00000000000",
    "imgur_gifv": "https://i.imgur.com/00000000.gifv",
    "redditbooru_gallery": "http://awwnime.redditbooru.com/gallery/000000/000000000/",
    "tumblr_link": "http://cowboy-bebop.tumblr.com/___/0000000",
    }

test_args = [ "--savedir", "testdir"
            , "--processes", "10"
            , "--subfolders"
            , "--subreddits", "test,testing"]

test_config = """
[redditcurl]
savedir = testdir
processes = 0
notitles = true
"""

test_config_auth = """
[oauth]
clientid = testid
redirect = http://testredirect
refresh_token = refreshtoken
access_token = accesstoken
"""


def create_submission(url="", title="", subreddit=""):
    submission = MagicMock()
    submission.url = url
    submission.title = title
    submission.subreddit.display_name = subreddit
    return submission


test_submissions = [create_submission(url, title, "testsubreddit") for title, url in test_links.items()]
test_downloaded = [(url, (lambda x: x != "fail")(title)) for title, url in test_links.items()]
# Creates a downloaded items list, with all test links as successfully downloaded except "fail" link.


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
