"""
    redditcurl, download the images you saved on Reddit.
    Copyright (C) 2014, 2015  Kaan Genç

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
import multiprocessing
import gzip
import argparse
import praw
from . import websites

# All file names will be translated according to _FILENAME_MAP, in order to remove characters
# that can't be used as the file name.
if sys.platform == "win32" or sys.platform == "cygwin":
    _FILENAME_MAP = {ord("/"): None,
                     ord("\\"): None,
                     ord("?"): None,
                     ord("*"): None,
                     ord(":"): None,
                     ord("|"): None,
                     ord("\""): None,
                     ord("<"): None,
                     ord(">"): None
                     }
else:
    _FILENAME_MAP = {ord("/"): None}


def manage_download(url, path, file_name=""):
    """Decide on the function to download the image and handle errors.

    The function should not raise any errors unless it is critical.
    Failure to download the image or find a suitable method will only
    make the function return False.

    Args:
        url: A url to an image or images. Depending on the website,
            a function will be picked.
        path: Path to the folder where image or images should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.

    Returns:
        True if download was completed successfully.
        Otherwise, False.
    """
    try:
        # websites module lists all supported downloaders under __all__
        for downloader in websites.__all__:
            if downloader.match(url):
                downloader.download(url, path, file_name)
                return url, True
        return url, False
    except (OSError, IOError, AttributeError, IndexError):
        return url, False


def download_submissions(submission_list, path, processes, use_titles=True, use_folders=True, only_from=[]):
    """Download all images in the submission_list to path.

    Args:
        submission_list: An iterable, containing praw.objects.Submission objects,
            or any other object that has .url and .title attributes.
        path: Path to the folder where images should be saved.
        processes: Number of processes to use for searching and downloading.
        use_titles: If set to True, titles of the submissions will be used
            as file names for the downloaded images.
        use_folders: If set to True, the images will be downloaded into folders
            based on their subreddits.
        only_from: If it is an empty list, then images from all subreddits will be downloaded.
            Otherwise, only images from the subreddits in this list will be downloaded.

    Returns:
        A list of tuples, containing the url of the image and True if the image was successfully downloaded,
        otherwise False.
    """
    download_queue = []
    used_folders = set()
    if use_titles:
        for sub in submission_list:
            if only_from == [] or sub.subreddit.display_name.casefold() in only_from:
                if use_titles:
                    # Using lstrip on the title to ensure that unix-like OS'es don't hide the files.
                    # Translate removes the characters that can't be used as file names.
                    title = sub.title.lstrip(".").translate(_FILENAME_MAP)
                else:
                    title = ""
                if use_folders:
                    folder = os.path.join(path, sub.subreddit.display_name)
                    # Keep track of folders to create missing ones later
                    used_folders.add(folder)
                else:
                    folder = path
                download_queue.append((sub.url, folder, title))
    for folder in used_folders:
        try:
            os.makedirs(folder)
        except (FileExistsError):
            pass
    if processes > 1:
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.starmap(manage_download, download_queue)
    else:
        results = [manage_download(*submission) for submission in download_queue]
    # Remove empty folders that have been created
    for folder in used_folders:
        try:
            os.removedirs(folder)
        except (OSError):
            pass
    return results


def filter_new(submission_list, downloaded_file):
    """Returns a list of images, removing the ones already saved.

    Args:
        submission_list: An iterable, containing praw.objects.Submission objects, or
            any object that has .url attribute.
        downloaded_file: Path to a .gz file, containing a list of downloaded pictures.
            If the file doesn't exist, it will be created.

    Returns:
        A list of praw.objects.Submission, containing only the submissions that
        haven't been downloaded yet.
    """
    try:
        with gzip.open(downloaded_file) as file:
            downloaded = file.read().decode("utf-8").split()
    except (FileNotFoundError):
        downloaded = []
    # Filter to allow only new link posts
    filtered = [submission for submission in submission_list
                if hasattr(submission, "url") and submission.url not in downloaded]
    return filtered


def update_new(saved_list, downloaded_file):
    """Adds the list of images to saved images file.

    Args:
        submission_list: An iterable, containing urls of saved images.
        downloaded_file: Path to a .gz file, containing a list of downloaded images.
            If the file doesn't exist, it will be created.
    """
    with gzip.open(downloaded_file, "ab") as file:
        file.write(("\n".join(saved_list)).encode("utf-8"))

def __main__():
    try:
        parser = argparse.ArgumentParser(description="Downloads your saved images from Reddit.")
        parser.add_argument("-u", "--username", type=str, required=True,
                            help="Reddit username.")
        parser.add_argument("-p", "--password", type=str, required=True,
                            help="Reddit password.")
        parser.add_argument("-d", "--savedir", type=str, required=True,
                            help="Directory to save the images.")
        parser.add_argument("-c", "--processes", type=int, default=20,
                            help="Number of processes to use. "
                                 "Use 1 to disable multiprocessing.")
        parser.add_argument("-b", "--subfolders", action="store_true", default=False,
                            help="Put the images into subfolders, based on their subreddits.")
        parser.add_argument("-t", "--subreddits", type=str, default="",
                            help="Only download from specific subreddits. Seperate names with commas (,).")
        parser.add_argument("-n", "--notitles", action="store_true", default=False,
                            help="Do not use titles of submissions as file names, "
                                 "use the names of downloaded files instead.")
        parser.add_argument("-f", "--savefile", type=str, default=".downloaded.gz",
                            help="The file to keep track of images that have been downloaded.")
        parser.add_argument("-r", "--remove", action="store_true", default=False,
                            help="Remove the files that were successfully downloaded from saved.")
        parser.add_argument("-s", "--silent", action="store_true", default=False,
                            help="Do not print anything about the scripts actions.")
        args = parser.parse_args()
        if args.silent:
            prints = lambda x: None
        else:
            prints = print
        if args.subreddits == "":
            subreddits = []
        else:
            subreddits = args.subreddits.strip(',').casefold().split(',')
            print("Downloading from {}".format(subreddits))
        r = praw.Reddit(user_agent="Just {} downloading some images".format(args.username))
        prints("Logging in as {}.".format(args.username))
        r.login(username=args.username, password=args.password)
        prints("Logged in.")
        prints("Getting data...")
        try:
            os.makedirs(args.savedir)
        except (FileExistsError):
            pass
        save_file = os.path.join(args.savedir, args.savefile)
        saved = filter_new(r.user.get_saved(limit=None), save_file)
        prints("Starting to download, using {} processes.".format(args.processes))
        downloaded = download_submissions(saved, args.savedir, args.processes,
                                          not args.notitles, args.subfolders, subreddits)
        prints("Processed {} urls.".format(len(downloaded)))
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
                if args.remove:
                    saved[i].unsave()
        prints("Updating saved files list.")
        update_new(successful_downloads, save_file)
        prints("\nDownloading finished.")
        prints("Successful: {} \t Failed: {}".format(success_count, fail_count))
    except (praw.errors.InvalidUserPass):
        print("Wrong password!")

if __name__ == "__init__":
    __main__()
