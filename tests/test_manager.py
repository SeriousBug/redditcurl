from unittest import mock
from tests import test_base
from redditcurl import manager


test_links = test_base.test_links


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
