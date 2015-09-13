import os
import tempfile
import unittest
import shutil
from unittest.mock import MagicMock


test_links = {
    "direct": "https://i.imgur.com/AaLX1Wn.jpg",
    "imgur_link": "https://imgur.com/AaLX1Wn",
    "imgur_album": "https://imgur.com/a/IEKXq",
    "imgur_gifv": "https://i.imgur.com/bJ0h81c.gifv",
    "redditbooru_gallery": "http://awwnime.redditbooru.com/gallery/nchg/chiyo-chan/",
    "tumblr_link": "http://cowboy-bebop.tumblr.com/post/111839970633",
    "fail": "https://github.com/SeriousBug/redditcurl"
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


def create_submission(url="", title="", subreddit=""):
    submission = MagicMock()
    submission.url = url
    submission.title = title
    submission.subreddit.display_name = subreddit
    return submission


test_submissions = [create_submission(url, title, "testsubreddit") for title, url in test_links.items()]


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
