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
        # Do try removing saved images, do not print anything
        scount, fcount, sdown = main.count_success(test_downloaded, True, (lambda x: None), mocked_saved)
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
