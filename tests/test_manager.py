import gzip
import json
import unittest
from unittest import mock
from tests import test_base
from redditcurl import manager


test_links = test_base.test_links
test_submissions = test_base.test_submissions


class TestManageDownload(test_base.EnterTemp):
    @mock.patch("redditcurl.websites.direct.download")
    def test_direct(self, mocked):
        manager.manage_download(test_links["direct"], "path", "file")
        mocked.assert_called_once_with(test_links["direct"], "path", "file")

    @mock.patch("redditcurl.websites.imgur_album.download")
    def test_imgur_album(self, mocked):
        manager.manage_download(test_links["imgur_album"], "path", "file")
        mocked.assert_called_once_with(test_links["imgur_album"], "path", "file")

    @mock.patch("redditcurl.websites.imgur_link.download")
    def test_imgur_link(self, mocked):
        manager.manage_download(test_links["imgur_link"], "path", "file")
        mocked.assert_called_once_with(test_links["imgur_link"], "path", "file")

    @mock.patch("redditcurl.websites.redditbooru_gallery.download")
    def test_redditbooru_gallery(self, mocked):
        manager.manage_download(test_links["redditbooru_gallery"], "path", "file")
        mocked.assert_called_once_with(test_links["redditbooru_gallery"], "path", "file")

    @mock.patch("redditcurl.websites.tumblr_link.download")
    def test_tumblr_link(self, mocked):
        manager.manage_download(test_links["tumblr_link"], "path", "file")
        mocked.assert_called_once_with(test_links["tumblr_link"], "path", "file")

    def test_failing_download(self):
        self.assertEqual(manager.manage_download(test_links["fail"], "path", "file"),
                         (test_links["fail"], False))

    def test_file_error(self):
        # Try downloading to a location that doesn't exist
        self.assertEqual(manager.manage_download(test_links["direct"], "doesnt/exist", "file"),
                         (test_links["direct"], False))


class TestUpdateNew(test_base.EnterTemp):
    def test_write_new(self):
        # Test with no existing file
        manager.update_new(list(test_base.test_links.values()), ".downloaded.gz")
        with gzip.open(".downloaded.gz", "rb") as file:
            self.assertEqual(list(test_base.test_links.values()), json.loads(file.read().decode("utf-8")))

    def test_write_existing(self):
        # Test with an existing file
        manager.update_new(list(test_links.values())[:3], ".downloaded.gz")
        manager.update_new(list(test_links.values())[3:], ".downloaded.gz")
        with gzip.open(".downloaded.gz", "rb") as file:
            self.assertEqual(list(test_links.values()), json.loads(file.read().decode("utf-8")))


class TestFilterNew(test_base.EnterTemp):
    def test_filter_new(self):
        # First, create a set to test with
        manager.update_new(list(test_links.values())[:3], ".downloaded.gz")
        filtered_items = manager.filter_new(test_submissions, ".downloaded.gz")
        self.assertTrue(len(test_submissions) > 0)
        self.assertTrue(len(filtered_items) > 0)
        for filtered, original in zip(filtered_items, test_submissions):
            self.assertEqual(filtered.url, original.url)
            self.assertEqual(filtered.title, original.title)
            self.assertEqual(filtered.subreddit.display_name, original.subreddit.display_name)
