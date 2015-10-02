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
import json
from redditcurl import websites
from redditcurl.exceptions import DownloadError
from requests.exceptions import RequestException


# All file names will be translated according to _FILENAME_MAP, in order to remove characters
# that can't be used as the file name.
if sys.platform == "win32" or sys.platform == "cygwin":
    _FILENAME_MAP = {ord("/"): " ",
                     ord("\\"): " ",
                     ord("?"): " ",
                     ord("*"): " ",
                     ord(":"): " ",
                     ord("|"): " ",
                     ord("\""): " ",
                     ord("<"): " ",
                     ord(">"): " "}
else:
    _FILENAME_MAP = {ord("/"): " "}


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
        for downloader in websites.downloaders:
            if downloader.match(url):
                downloader.download(url, path, file_name)
                return url, True
        return url, False
    except (OSError, IOError, AttributeError, IndexError, ValueError, DownloadError, RequestException):
        return url, False


def download_info(submission, path, use_titles, use_folders):
    """Return the download information for the given submission."""
    if use_titles:
        # Using lstrip on the title to ensure that unix-like OS'es don't hide the files.
        # Translate removes the characters that can't be used as file names.
        title = submission.title.lstrip(".").translate(_FILENAME_MAP)
    else:
        title = ""
    if use_folders:
        folder = os.path.join(path, submission.subreddit.display_name)
    else:
        folder = path
    return folder, title


def process_submissions(submission_list, path, use_titles, use_folders, only_from):
    """Process the submission list, generating a download queue and a list of folders to be used.."""
    download_queue = []
    used_folders = set()
    for sub in submission_list:
        if only_from == [] or sub.subreddit.display_name.casefold() in only_from:
            folder, title = download_info(sub, path, use_titles, use_folders)
            download_queue.append((sub.url, folder, title))
            # Keep track of folders to create missing ones later
            used_folders.add(folder)
    return download_queue, used_folders


def make_folders(used_folders):
    """Create the folders that will be possibly used."""
    for folder in used_folders:
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass


def cleanup_folders(used_folders):
    """Delete the folders that were not used."""
    for folder in used_folders:
        try:
            os.removedirs(folder)
        except OSError:
            pass


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
    download_queue, used_folders = process_submissions(submission_list, path, use_titles, use_folders, only_from)
    make_folders(used_folders)
    if processes > 1:
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.starmap(manage_download, download_queue)
    else:
        results = [manage_download(*submission) for submission in download_queue]
    cleanup_folders(used_folders)
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
            downloaded = set(json.loads(file.read().decode("utf-8")))
    except FileNotFoundError:
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
    try:
        with gzip.open(downloaded_file, "rb") as file:
            old_list = json.loads(file.read().decode("utf-8"))
    except FileNotFoundError:
        old_list = []
    with gzip.open(downloaded_file, "wb") as file:
        file.write(json.dumps(old_list + saved_list).encode("utf-8"))
