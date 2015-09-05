import os
import argparse
import configparser
import praw
from redditcurl import manager


DEFAULTS = {"processes":  "20",
            "subfolders": "false",
            "subreddits": "",
            "notitles":   "false",
            "savefile":   ".downloaded.gz",
            "remove":     "false",
            "silent":     "false"
}


class ConfigError(Exception):
    """The exception which is raised when a required configuration was not set."""
    pass


def setup_parser():
    """Setup the argument parser.

    The function sets up and returns the argument parser.

    Returns:
        The argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(description="Downloads your saved images from Reddit.")
    parser.add_argument("-u", "--username", type=str,
                        help="Reddit username.")
    parser.add_argument("-p", "--password", type=str,
                        help="Reddit password.")
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
    return {k: str(v) for k, v in vars(args).items() if not (v is None or v is  False)}
    

def get_config(args):
    """Decide on the program configuration.

    This function uses, in this order, the built-in defaults, the configuration file,
    and the command line arguments to decide the program configuration. The latter
    ones will override the former ones.

    Args:
        args: An argparse.Namespace object, normally built by parse_args function.

    Returns:
        A dictionary, containing the settings for the application.
        The keys of the dictionary are same as the arguments the
        program accepts, minus the dashes before them.

    Raises:
        If one of the required options are missing, a ConfigError will be raised.
    """
    config = configparser.ConfigParser()
    config.read_dict({"redditcurl": DEFAULTS})
    config_file = find_config()
    config.read(config_file)
    config.read_dict({"redditcurl": args2dict(args)})
    # Check if the required fields have been filled
    final_config = config["redditcurl"]
    if not "username" in final_config:
        raise ConfigError("No username set!")
    if not "password" in final_config:
        raise ConfigError("No password set!")
    if not "savedir" in final_config:
        raise ConfigError("No save directory set!")
    return final_config


def count_success(downloaded, remove, prints):
    """Count the successful downloads."""
    success_count = 0
    fail_count = 0
    successful_downloads = []
    for i, submission in enumerate(downloaded):
        url, successful = submission
        if not successful:
            fail_count += 1
            prints("Download failed: {}".format(url))
        else:  # successful
            success_count += 1
            successful_downloads.append(url)
            if remove:
                saved[i].unsave()
    return success_count, fail_count, successful_downloads


def __main__():
    try:
        args = setup_parser().parse_args()
        conf = get_config(args)
        if conf.getboolean("silent"):
            prints = lambda x: None
        else:
            prints = print
        if conf.get("subreddits") == "":
            subreddits = []
        else:
            subreddits = conf.get("subreddits").strip(',').casefold().split(',')
            prints("Downloading from {}".format(', '.join(subreddits)))
        r = praw.Reddit(user_agent="Just {} downloading some images".format(conf.get("username")))
        prints("Logging in as {}.".format(conf.get("username")))
        r.login(username=conf.get("username"), password=conf.get("password"), disable_warning=True)
        prints("Logged in.")
        prints("Getting data...")
        try:
            os.makedirs(conf.get("savedir"))
        except (FileExistsError):
            # If the save directory exists, we don't need to create it
            pass
        save_file = os.path.join(conf.get("savedir"), conf.get("savefile"))
        saved = manager.filter_new(r.user.get_saved(limit=None), save_file)
        prints("Starting to download, using {} processes.".format(conf.get("processes")))
        downloaded = manager.download_submissions(saved, conf.get("savedir"), conf.getint("processes"),
                                                  not conf.getboolean("notitles"),
                                                  conf.getboolean("subfolders"), subreddits)
        prints("Processed {} urls.".format(len(downloaded)))
        remove = conf.getboolean("remove")
        success_count, fail_count, successful_downloads = count_success(downloaded, remove, prints)
        prints("Updating saved files list.")
        manager.update_new(successful_downloads, save_file)
        prints("\nDownloading finished.")
        prints("Successful: {} \t Failed: {}".format(success_count, fail_count))
    except (praw.errors.InvalidUserPass):
        print("Wrong password!")
    except (ConfigError) as err:
        print(err)


if __name__ == "__main__":
    __main__()
