"""
    redditcurl, download the images you saved on Reddit.
    Copyright (C) 2015  Kaan Genç

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import logging
import argparse
import configparser
import praw
import requests
from redditcurl import manager
from redditcurl.websites import shared_config
from redditcurl.exceptions import ConfigError


DEFAULTS = {"processes":  "20",
            "subfolders": "false",
            "subreddits": "",
            "notitles":   "false",
            "prefer-mp4": "false",
            "savefile":   ".downloaded.gz",
            "remove":     "false",
            "silent":     "false"}

OAUTH_DEFAULTS = {"clientid": "Fp9ci3HipOW1FQ",
                  "redirect": "http://kaangenc.me/static/redditcurl.html"}

OAUTH_SCOPES = {"identity", "history"}


def setup_parser():
    """Setup the argument parser.

    The function sets up and returns the argument parser.

    Returns:
        The argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(description="Downloads your saved images from Reddit.")
    parser.add_argument("-d", "--savedir", type=str,
                        help="Directory to save the images.")
    parser.add_argument("-c", "--processes", type=int,
                        help="Number of processes to use."
                        "Use 1 to disable multiprocessing.")
    parser.add_argument("-b", "--subfolders", action="store_true",
                        help="Put the images into subfolders, based on their subreddits.")
    parser.add_argument("-t", "--subreddits", type=str,
                        help="Only download from specific subreddits. Seperate names with commas (,).")
    parser.add_argument("-n", "--notitles", action="store_true",
                        help="Do not use titles of submissions as file names, "
                        "use the names of downloaded files instead.")
    parser.add_argument("-m", "--prefer-mp4", action="store_true",
                        help="In gfycat and imgur gifv links, download mp4's instead of webm.")
    parser.add_argument("-f", "--savefile", type=str,
                        help="The file to keep track of images that have been downloaded.")
    parser.add_argument("-r", "--remove", action="store_true",
                        help="Remove the files that were successfully downloaded from saved.")
    parser.add_argument("-s", "--silent", action="store_true",
                        help="Do not print anything about the scripts actions.")
    return parser


def find_config():
    """Find the configuration file."""
    home = os.path.expanduser("~")
    config_dir = os.getenv("XDG_CONFIG_HOME",
                           default=os.path.join(home, ".config"))
    return os.path.join(config_dir, "redditcurl")


def args2dict(args):
    """Convert the arguments into a dictionary to be read by ConfigParser.

    The values that are not set in the command line, meaning the ones that are None
    or False are skipped. All values are turned into strings, so that ConfigParser
    can read them."""
    return {k: str(v) for k, v in vars(args).items() if not (v is None or v is False)}


def get_config(args, config_file):
    """Decide on the program configuration.

    This function uses, in this order, the built-in defaults, the configuration file,
    and the command line arguments to decide the program configuration. The latter
    ones will override the former ones.

    Args:
        args: An argparse.Namespace object, normally built by parse_args function.
        config_parser: A string, showing the path to the configuration file.

    Returns:
        A dictionary, containing the settings for the application.
        The keys of the dictionary are same as the arguments the
        program accepts, minus the dashes before them.

    Raises:
        If one of the required options are missing, a ConfigError will be raised.
    """
    config = configparser.ConfigParser()
    config.read_dict({"redditcurl": DEFAULTS})
    config.read_dict({"oauth": OAUTH_DEFAULTS})
    config.read(config_file)
    config.read_dict({"redditcurl": args2dict(args)})
    # Check if the required fields have been filled
    if "savedir" not in config["redditcurl"]:
        raise ConfigError("No save directory set!")
    return config


def count_success(downloaded, remove, saved):
    """Count the successful downloads."""
    logger = logging.getLogger("main")
    success_count = 0
    fail_count = 0
    successful_downloads = []
    for i, submission in enumerate(downloaded):
        url, successful = submission
        if not successful:
            fail_count += 1
            logger.warning("Download failed: {}".format(url))
        else:  # successful
            success_count += 1
            successful_downloads.append(url)
            if remove:
                saved[i].unsave()
    return success_count, fail_count, successful_downloads


def is_authenticated(conf):
    """Returns True if the user has OAuth2 tokens set up, False otherwise."""
    return all(("access_token" in conf, "refresh_token" in conf))


def setup_logger(name, silent):
    """Setup a logger to handle information and error messages.

    Info messages are printed to stdout, without any formatting.
    Other messages, such as errors or debug messages are written to
    stderr alongside log level and logger name.

    Args:
        name: The name of the logger, used in warning, error and debug messages.
        silent: If true, info messages won't be printed.
    Returns:
        A logging.Logger object, which can be used with the methods such as
        info, warning and error to print messages.
    """
    if silent:
        loglevel = logging.WARNING
    else:
        loglevel = logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    # Logging for info messages
    info_handler = logging.StreamHandler(stream=sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter("%(message)s")
    info_handler.setFormatter(info_formatter)
    info_handler.addFilter(lambda r: r.levelno == logging.INFO)
    # Logging for error messages
    err_handler = logging.StreamHandler(stream=sys.stderr)
    err_handler.setLevel(logging.DEBUG)
    err_formatter = logging.Formatter("%(levelname)s - %(name)s: %(message)s")
    err_handler.setFormatter(err_formatter)
    err_handler.addFilter(lambda r: r.levelno != logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(err_handler)
    return logger


def __main__():
    try:
        args = setup_parser().parse_args()
        conf_path = find_config()
        conf = get_config(args, conf_path)
        conf_r = conf["redditcurl"]
        conf_o = conf["oauth"]
        logger = setup_logger("main", conf_r.getboolean("silent"))
        if conf_r.get("subreddits") == "":
            subreddits = []
        else:
            subreddits = conf_r.get("subreddits").strip(',').casefold().split(',')
            logger.info("Downloading from {}".format(', '.join(subreddits)))
        if conf_r.getboolean("prefer-mp4"):
            shared_config.PREFER_WEBM = False
        logger.info("Connecting to Reddit.")
        r = praw.Reddit(user_agent="redditcurl")
        r.set_oauth_app_info(client_id=conf_o.get("clientid"),
                             redirect_uri=conf_o.get("redirect"),
                             client_secret="None")
        if not is_authenticated(conf_o):
            auth_url = r.get_authorize_url("state", OAUTH_SCOPES, True)
            print("Please visit {} to authorize access to your account history.".format(auth_url))
            auth_code = input("Enter the code: ")
            access_information = r.get_access_information(auth_code)
            conf.read_dict({"oauth":
                            {"refresh_token": access_information["refresh_token"],
                             "access_token": access_information["access_token"]}})
            with open(conf_path, "w") as conf_file:
                conf.write(conf_file)
        else:
            r.set_access_credentials(scope=OAUTH_SCOPES,
                                     access_token=conf_o.get("access_token"),
                                     refresh_token=conf_o.get("refresh_token"))
            logger.info("Refreshing access token.")
            r.refresh_access_information(conf_o.get("refresh_token"))
            # We don't save the new access_token here, since we refresh it every time the program is run
        logger.info("Getting data...")
        try:
            os.makedirs(conf_r.get("savedir"))
        except FileExistsError:
            # If the save directory exists, we don't need to create it
            pass
        save_file = os.path.join(conf_r.get("savedir"), conf_r.get("savefile"))
        saved = manager.filter_new(r.user.get_saved(limit=None), save_file)
        logger.info("Starting to download, using {} processes.".format(conf_r.get("processes")))
        downloaded = manager.download_submissions(saved, conf_r.get("savedir"), conf_r.getint("processes"),
                                                  not conf_r.getboolean("notitles"),
                                                  conf_r.getboolean("subfolders"), subreddits)
        logger.info("Processed {} urls.".format(len(downloaded)))
        remove = conf_r.getboolean("remove")
        success_count, fail_count, successful_downloads = count_success(downloaded, remove, saved)
        logger.info("Updating saved files list.")
        manager.update_new(successful_downloads, save_file)
        logger.info("\nDownloading finished.")
        logger.info("Successful: {} \t Failed: {}".format(success_count, fail_count))
    except (praw.errors.PRAWException,
            requests.exceptions.RequestException) as err:
        logger.error(err)
    except ConfigError as err:
        # When a ConfigError occurs, the logger isn't set up yet, so use the default logger
        logging.error(err)


if __name__ == "__main__":
    __main__()
