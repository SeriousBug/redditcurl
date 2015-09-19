import os
import gzip
import json
import unittest
from unittest import mock
from tests import test_base
from redditcurl import manager


test_links = test_base.test_links
test_links_404 = test_base.test_links_404
test_submissions = test_base.test_submissions
original_urls = [submission.url for submission in test_submissions]
original_titles = [submission.title for submission in test_submissions]
original_subreddits = [submission.subreddit.display_name for submission in test_submissions]


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


class TestManageDownloadErrors(test_base.EnterTemp):
    def test_direct(self):
        self.assertEqual(manager.manage_download(test_links_404["direct"], "path", "file"),
                         (test_links_404["direct"], False))

    def test_gfycat(self):
        self.assertEqual(manager.manage_download(test_links_404["gfycat"], "path", "file"),
                         (test_links_404["gfycat"], False))

    def test_imgur_album(self):
        self.assertEqual(manager.manage_download(test_links_404["imgur_album"], "path", "file"),
                         (test_links_404["imgur_album"], False))

    def test_imgur_link(self):
        self.assertEqual(manager.manage_download(test_links_404["imgur_link"], "path", "file"),
                         (test_links_404["imgur_link"], False))

    def test_redditbooru_gallery(self):
        self.assertEqual(manager.manage_download(test_links_404["redditbooru_gallery"], "path", "file"),
                         (test_links_404["redditbooru_gallery"], False))

    def test_tumblr_link(self):
        self.assertEqual(manager.manage_download(test_links_404["tumblr_link"], "path", "file"),
                         (test_links_404["tumblr_link"], False))

    def test_deviantart(self):
        self.assertEqual(manager.manage_download(test_links_404["deviantart"], "path", "file"),
                         (test_links_404["deviantart"], False))

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
        for filtered in filtered_items:
            self.assertTrue(filtered.url in original_urls)
            self.assertTrue(filtered.title in original_titles)
            self.assertTrue(filtered.subreddit.display_name in original_subreddits)

    def test_filter_new_empty(self):
        # Test filter new without a downloaded file
        filtered_items = manager.filter_new(test_submissions, ".downloaded.gz")
        self.assertTrue(len(filtered_items) == len(test_links))
        for filtered in filtered_items:
            self.assertTrue(filtered.url in original_urls)
            self.assertTrue(filtered.title in original_titles)
            self.assertTrue(filtered.subreddit.display_name in original_subreddits)


class TestDownloadInfo(unittest.TestCase):
    def test_title_folder(self):
        # Any submission will do, no logic tied to submission itself here
        submission = test_base.create_submission(title="test title", subreddit="testsubreddit")
        folder, title = manager.download_info(submission, "testfolder", True, True)
        self.assertEqual(folder, os.path.join("testfolder", "testsubreddit"))
        self.assertEqual(title, "test title")

    def test_notitle_nofolder(self):
        submission = test_base.create_submission(title="test title", subreddit="testsubreddit")
        folder, title = manager.download_info(submission, "testfolder", False, False)
        self.assertEqual(folder, "testfolder")
        self.assertEqual(title, "")

    def test_special_title(self):
        submission = test_base.create_submission(title=".title w/ special characters", subreddit="testsubreddit")
        folder, title = manager.download_info(submission, "testfolder", True, True)
        self.assertEqual(title, "title w special characters")


class TestMakeFolders(test_base.EnterTemp):
    def test_make_folders(self):
        manager.make_folders(["testfolder", "otherfolder", "sub"])
        self.assertTrue(os.path.isdir("testfolder"))
        self.assertTrue(os.path.isdir("otherfolder"))
        self.assertTrue(os.path.isdir("sub"))

    def test_make_subfolders(self):
        manager.make_folders(["testfolder/subfolder", "testfolder/otherfolder"])
        self.assertTrue(os.path.isdir("testfolder"))
        self.assertTrue(os.path.isdir("testfolder/subfolder"))
        self.assertTrue(os.path.isdir("testfolder/otherfolder"))


class TestCleanupFolders(test_base.EnterTemp):
    def test_cleanup_folders(self):
        os.makedirs("testfolder")
        os.makedirs("otherfolder")
        manager.cleanup_folders(["testfolder", "otherfolder"])
        self.assertFalse(os.path.isdir("testfolder"))
        self.assertFalse(os.path.isdir("otherfolder"))

    def test_cleanup_nonempty(self):
        # Set up a folder and touch a file in it
        os.makedirs("testfolder")
        open("testfolder/testfile", "w").close()
        manager.cleanup_folders(["testfolder"])
        # Shouldn't get cleaned up since it isn't empty
        self.assertTrue(os.path.isdir("testfolder"))


class TestProcessSubmission(unittest.TestCase):
    def test_process_all(self):
        download_queue, used_folders = manager.process_submissions(test_submissions, ".", True, True, [])
        # Checking for only_from, ensure that none got filtered
        for url, folder, title in download_queue:
            self.assertTrue(url in original_urls)
        self.assertEqual(len(download_queue), len(test_submissions))

    def test_process_only_from(self):
        download_queue, used_folders = manager.process_submissions(test_submissions, ".", True, True, ["testsubreddit"])
        # All must have passed again, all submissions are from correct subreddit
        for url, folder, title in download_queue:
            self.assertTrue(url in original_urls)
        self.assertEqual(len(download_queue), len(test_submissions))

    def test_process_nowhere(self):
        download_queue, used_folders = manager.process_submissions(test_submissions, ".", True, True, ["nowhere"])
        # None should pass, all are from wrong subreddit
        self.assertEqual(len(download_queue), 0)


class TestDownloadSubmission(test_base.EnterTemp):
    @mock.patch("redditcurl.manager.manage_download")
    @mock.patch("redditcurl.manager.make_folders")
    @mock.patch("redditcurl.manager.cleanup_folders")
    def test_single_thread(self, mocked_cleanup, mocked_make, mocked_download):
        mocked_download.return_value = ("", True)
        results = manager.download_submissions(test_submissions, ".", 1, use_titles=True, use_folders=False)
        self.assertTrue(len(results) == len(test_submissions))
        expected_download_calls = [mock.call(sub.url, ".", sub.title) for sub in test_submissions]
        mocked_download.assert_has_calls(expected_download_calls, any_order=True)

    @mock.patch("multiprocessing.pool.Pool.starmap")
    @mock.patch("redditcurl.manager.make_folders")
    @mock.patch("redditcurl.manager.cleanup_folders")
    def test_multi_thread(self, mocked_cleanup, mocked_make, mocked_starmap):
        manager.download_submissions(test_submissions, ".", 2, use_titles=True, use_folders=False)
        expected_queue, expected_folders = manager.process_submissions(test_submissions, ".",
                                                                       use_titles=True,
                                                                       use_folders=False,
                                                                       only_from=[])
        mocked_starmap.assert_called_once_with(manager.manage_download, expected_queue)
