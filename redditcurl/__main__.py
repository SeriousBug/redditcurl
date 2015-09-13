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

OAUTH_DEFAULTS = {"clientid": "Fp9ci3HipOW1FQ",
                  "redirect": "http://kaangenc.me/static/redditcurl.html"
}

OAUTH_SCOPES = {"identity", "history"}

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
    if not "savedir" in config["redditcurl"]:
        raise ConfigError("No save directory set!")
    return config


def count_success(downloaded, remove, prints, saved):
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


def is_authenticated(conf):
    """Returns True if the user has OAuth2 tokens set up, False otherwise."""
    return all(("access_token" in conf, "refresh_token" in conf))


def __main__():
    try:
        args = setup_parser().parse_args()
        conf_path = find_config()
        conf = get_config(args, conf_path)
        conf_r = conf["redditcurl"]
        conf_o = conf["oauth"]
        if conf_r.getboolean("silent"):
            prints = lambda x: None
        else:
            prints = print
        if conf_r.get("subreddits") == "":
            subreddits = []
        else:
            subreddits = conf_r.get("subreddits").strip(',').casefold().split(',')
            prints("Downloading from {}".format(', '.join(subreddits)))
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
                             "access_token": access_information["access_token"]}
            })
            with open(conf_path, "w") as conf_file:
                conf.write(conf_file)
        else:
            r.set_access_credentials(scope=OAUTH_SCOPES,
                                     access_token=conf_o.get("access_token"),
                                     refresh_token=conf_o.get("refresh_token"))
            prints("Refreshing access token.")
            r.refresh_access_information(conf_o.get("refresh_token"))
            # We don't save the new access_token here, since we refresh it every time the program is run
        prints("Getting data...")
        try:
            os.makedirs(conf_r.get("savedir"))
        except (FileExistsError):
            # If the save directory exists, we don't need to create it
            pass
        save_file = os.path.join(conf_r.get("savedir"), conf_r.get("savefile"))
        saved = manager.filter_new(r.user.get_saved(limit=None), save_file)
        prints("Starting to download, using {} processes.".format(conf_r.get("processes")))
        downloaded = manager.download_submissions(saved, conf_r.get("savedir"), conf_r.getint("processes"),
                                                  not conf_r.getboolean("notitles"),
                                                  conf_r.getboolean("subfolders"), subreddits)
        prints("Processed {} urls.".format(len(downloaded)))
        remove = conf_r.getboolean("remove")
        success_count, fail_count, successful_downloads = count_success(downloaded, remove, prints, saved)
        prints("Updating saved files list.")
        manager.update_new(successful_downloads, save_file)
        prints("\nDownloading finished.")
        prints("Successful: {} \t Failed: {}".format(success_count, fail_count))
    except (ConfigError) as err:
        print(err)


if __name__ == "__main__":
    __main__()
