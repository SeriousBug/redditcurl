import os
import unittest
from unittest import mock
from tests import test_base
from redditcurl import __main__ as main


test_args = test_base.test_args
test_config = test_base.test_config

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
