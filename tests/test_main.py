import os
import unittest
from unittest import mock
from tests import test_base
from redditcurl import __main__ as main


test_links = test_base.test_links
test_args = test_base.test_args
test_config = test_base.test_config
test_downloaded = test_base.test_downloaded


class TestArguments(unittest.TestCase):
    def test_args2dict(self):
        parser = main.setup_parser()
        args = parser.parse_args(test_args)
        argdict = main.args2dict(args)
        self.assertEqual(argdict["savedir"], "testdir")
        self.assertEqual(argdict["processes"], "10")
        self.assertEqual(argdict["subfolders"], "True")
        self.assertEqual(argdict["subreddits"], "test,testing")

    def test_parser_empty(self):
        parser = main.setup_parser()
        args = parser.parse_args([])
        argdict = main.args2dict(args)
        # Ensure that args2dict skips empty arguments
        self.assertEqual(len(argdict), 0)




class TestConfig(test_base.EnterTemp):
    @mock.patch("os.getenv")
    def test_find_config(self, mocked):
        mocked.return_value = "test_config_home"
        config = main.find_config()
        self.assertEqual(config, os.path.join("test_config_home", "redditcurl"))

    def test_config_noargs_noconfig(self):
        args = main.setup_parser().parse_args([])
        with self.assertRaises(main.ConfigError):
            main.get_config(args, "no-config-file")

    def test_config_args_noconfig(self):
        args = main.setup_parser().parse_args(test_args)
        conf = main.get_config(args, "no-config-file")["redditcurl"]
        self.assertEqual(conf.get("savedir"), "testdir")
        self.assertEqual(conf.getint("processes"), 10)
        self.assertTrue(conf.getboolean("subfolders"))
        self.assertFalse(conf.getboolean("notitles"))

    def test_config_noargs_config(self):
        args = main.setup_parser().parse_args([])
        # Setting up a config file first
        with open("testconfig", "w") as conf_file:
            conf_file.write(test_config)
        conf = main.get_config(args, "testconfig")["redditcurl"]
        self.assertEqual(conf.get("savedir"), "testdir")
        self.assertEqual(conf.getint("processes"), 0)
        self.assertFalse(conf.getboolean("subfolders"))
        self.assertTrue(conf.getboolean("notitles"))

    def test_config_args_config(self):
        args = main.setup_parser().parse_args(test_args)
        with open("testconfig", "w") as conf_file:
            conf_file.write(test_config)
        conf = main.get_config(args, "testconfig")["redditcurl"]
        self.assertEqual(conf.get("savedir"), "testdir")
        self.assertEqual(conf.getint("processes"), 10)
        self.assertTrue(conf.getboolean("subfolders"))
        self.assertTrue(conf.getboolean("notitles"))


class TestCountSuccess(unittest.TestCase):
    def test_count_success(self):
        mocked_saved = mock.MagicMock()
        # Do try removing saved images
        scount, fcount, sdown = main.count_success(test_downloaded, True, mocked_saved)
        # There should be only a single failed link, see test_base.mocked_saved
        self.assertEqual(scount, len(test_links) - 1)
        self.assertEqual(fcount, 1)
        self.assertEqual(len(sdown), len(test_links) - 1)
        self.assertNotIn(test_links["fail"], sdown)
        # Make sure everything except the failed link was deleted.
        # The function should only access them if it is going to unsave them, so checking that is enough.
        self.assertEqual(mocked_saved.__getitem__.call_count, len(test_links) - 1)
        fail_index = test_downloaded.index((test_links["fail"], False))
        self.assertNotIn(mock.call(fail_index), mocked_saved.__getitem__.call_args_list)


class TestMain(test_base.EnterTemp):
    @mock.patch("builtins.input")
    @mock.patch("praw.Reddit")
    @mock.patch("os.environ")
    @mock.patch("redditcurl.__main__.setup_parser")
    @mock.patch("redditcurl.__main__.count_success")
    @mock.patch("redditcurl.manager.download_submissions")
    @mock.patch("redditcurl.manager.update_new")
    def test_main_noauth(self, mocked_update, mocked_download,
                         mocked_count, mocked_parser, mocked_environ,
                         mocked_praw, mocked_input):
        # Mock the argument parser
        mocked_parser.return_value.parse_args.return_value.__dict__ = {"savedir": "sub",
                                                                       "processes": 5,
                                                                       "silent": False,}
        mocked_input.return_value = "auth code"
        mocked_reddit = mocked_praw.return_value
        mocked_reddit.get_access_information.return_value = {"refresh_token": "refresh token",
                                                             "access_token": "access token"}
        # Mock the configuration directory to be the current temporary directory
        mocked_environ.get.return_value = os.getcwd()
        mocked_reddit.user.get_saved.return_value = test_base.test_submissions
        mocked_download.return_value = test_base.test_downloaded
        mocked_count.return_value = (0, 0, [])
        main.__main__()
        # Check if the authentication tokens were saved
        self.assertTrue(os.path.isfile(os.path.join(os.getcwd(), "redditcurl")))
        mocked_reddit.get_access_information.assert_called_once_with("auth code")
        mocked_reddit.user.get_saved.assert_called_once_with(limit=None)
        mocked_download.assert_called_once_with(test_base.test_submissions,
                                                "sub", 5, True, False, [])
        # We can't really check the other args
        mdownloaded, mremove, _ = mocked_count.call_args[0]
        self.assertEqual((mdownloaded, mremove), (test_base.test_downloaded, False))

    @mock.patch("praw.Reddit")
    @mock.patch("os.environ")
    @mock.patch("redditcurl.__main__.setup_parser")
    @mock.patch("redditcurl.__main__.count_success")
    @mock.patch("redditcurl.manager.download_submissions")
    @mock.patch("redditcurl.manager.update_new")
    def test_main_auth(self, mocked_update, mocked_download,
                       mocked_count, mocked_parser, mocked_environ,
                       mocked_praw):
        # Mock the argument parser
        mocked_parser.return_value.parse_args.return_value.__dict__ = {"savedir": "sub",
                                                                       "processes": 5,
                                                                       "silent": True}
        mocked_reddit = mocked_praw.return_value
        # Mock the configuration directory to be the current temporary directory
        mocked_environ.get.return_value = os.getcwd()
        # Write a test configuration
        with open("redditcurl", "w") as conf_file:
            conf_file.write(test_base.test_config_auth)
        mocked_reddit.user.get_saved.return_value = test_base.test_submissions
        mocked_download.return_value = test_base.test_downloaded
        mocked_count.return_value = (0, 0, [])
        main.__main__()
        # Check if the authentication tokens were saved
        self.assertTrue(os.path.isfile(os.path.join(os.getcwd(), "redditcurl")))
        mocked_reddit.set_access_credentials.assert_called_once_with(scope=main.OAUTH_SCOPES,
                                                                     access_token="accesstoken",
                                                                     refresh_token="refreshtoken")
        mocked_reddit.refresh_access_information.assert_called_once_with("refreshtoken")
        mocked_reddit.user.get_saved.assert_called_once_with(limit=None)
        mocked_download.assert_called_once_with(test_base.test_submissions,
                                                "sub", 5, True, False, [])
        # We can't really check the other args
        mdownloaded, mremove, _ = mocked_count.call_args[0]
        self.assertEqual((mdownloaded, mremove), (test_base.test_downloaded, False))

    @mock.patch("praw.Reddit")
    @mock.patch("os.environ")
    @mock.patch("redditcurl.__main__.setup_parser")
    @mock.patch("redditcurl.__main__.count_success")
    @mock.patch("redditcurl.manager.download_submissions")
    @mock.patch("redditcurl.manager.update_new")
    def test_main_subs_mp4(self, mocked_update, mocked_download,
                           mocked_count, mocked_parser, mocked_environ,
                           mocked_praw):
        # Mock the argument parser
        mocked_parser.return_value.parse_args.return_value.__dict__ = {"savedir": "sub",
                                                                       "processes": 5,
                                                                       "silent": True,
                                                                       "prefer-mp4": True,
                                                                       "subreddits": "testsubreddit,test,example,"}
        mocked_reddit = mocked_praw.return_value
        # Mock the configuration directory to be the current temporary directory
        mocked_environ.get.return_value = os.getcwd()
        # Write a test configuration
        with open("redditcurl", "w") as conf_file:
            conf_file.write(test_base.test_config_auth)
        mocked_reddit.user.get_saved.return_value = test_base.test_submissions
        mocked_download.return_value = test_base.test_downloaded
        mocked_count.return_value = (0, 0, [])
        main.__main__()
        mocked_reddit.set_access_credentials.assert_called_once_with(scope=main.OAUTH_SCOPES,
                                                                     access_token="accesstoken",
                                                                     refresh_token="refreshtoken")
        mocked_reddit.refresh_access_information.assert_called_once_with("refreshtoken")
        mocked_reddit.user.get_saved.assert_called_once_with(limit=None)
        mocked_download.assert_called_once_with(test_base.test_submissions,
                                                "sub", 5, True, False, ["testsubreddit", "test", "example"])
        # We can't really check the other args
        mdownloaded, mremove, _ = mocked_count.call_args[0]
        self.assertEqual((mdownloaded, mremove), (test_base.test_downloaded, False))
        # Note that we don't check if redditcurl.websites.shared_config.PREFER_MP4 was set.
        # TODO: It might be a good idea to refactor how configuration should be passed to the
        # downloaders.

    @mock.patch("praw.Reddit")
    @mock.patch("os.environ")
    @mock.patch("redditcurl.__main__.setup_parser")
    @mock.patch("redditcurl.__main__.count_success")
    @mock.patch("redditcurl.manager.download_submissions")
    @mock.patch("redditcurl.manager.update_new")
    def test_main_config_error(self, mocked_update, mocked_download,
                           mocked_count, mocked_parser, mocked_environ,
                           mocked_praw):
        # Mock the argument parser
        mocked_parser.return_value.parse_args.return_value.__dict__ = {"processes": 5,
                                                                       "silent": True}
        mocked_reddit = mocked_praw.return_value
        # Mock the configuration directory to be the current temporary directory
        mocked_environ.get.return_value = os.getcwd()
        # Write a test configuration
        with open("redditcurl", "w") as conf_file:
            conf_file.write(test_base.test_config_auth)
        mocked_reddit.user.get_saved.return_value = test_base.test_submissions
        mocked_download.return_value = test_base.test_downloaded
        mocked_count.return_value = (0, 0, [])
        main.__main__()
        # The main should exit early because savedir is not set, nothing should run
        mocked_reddit.set_access_credentials.assert_not_called()
        mocked_reddit.refresh_access_information.assert_not_called()
        mocked_reddit.user.get_saved.assert_not_called()
        mocked_download.assert_not_called()
        mocked_count.assert_not_called()

