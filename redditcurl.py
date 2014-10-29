"""
    redditcurl, download the images you saved on Reddit.
    Copyright (C) 2014  Kaan Genç

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
import argparse
import tempfile
import shutil
import multiprocessing
from zipfile import ZipFile
import requests
import praw
from bs4 import BeautifulSoup

IMAGE_FORMATS = ['bmp', 'dib', 'eps', 'ps', 'gif', 'im', 'jpg', 'jpe', 'jpeg',
                 'pcd', 'pcx', 'png', 'pbm', 'pgm', 'ppm', 'psd', 'tif',
                 'tiff', 'xbm', 'xpm', 'rgb', 'rast', 'svg']


def is_direct_image(url):
    """Check if the given string leads to an image file.

    The check is done by checking the extension at the end of the string,
    No check is done to see if file (or page) actually exists, or if it
    is really an image file.

    Args:
        url: A file path or url as string.

    Returns:
        True if the string ends with a known image extension.
        False otherwise.
    """
    if url.split('.')[-1] in IMAGE_FORMATS:
        return True
    return False


def download(url, path, file_name=""):
    """Download the file at url to path if it doesn't exist.

    Correct file extension will be given based on the response header.
    Byte mode is used for Windows.

    Args:
        url: A url to the file. Should start with http:// or https://.
        path: Path to the folder where the file should be saved.
        file_name: The file name to use when saving the file.
            file_name is an empty string, then name of the downloaded file will be used.
    """
    response = requests.get(url)
    if file_name == "":
        base_name = url.split('/')[-1].split('.')[-1]
    else:
        base_name = file_name
    extension = response.headers["Content-Type"].split('/')[-1]
    with open("{}/{}.{}".format(path, base_name, extension), mode="wb") as file:
        file.write(response.content)


def imgur_album(url, path, file_name=""):
    """Download an album from imgur.

    The album is downloaded as a zip archive and extracted to path.

    Args:
        url: A url to an imgur album.
        path: Path to the folder where the images should be saved.
        file_name: File name to use when saving the images.
            A number will be appended to the end of the name for
            each image in the album.
            If file_name is an empty string, the files will keep
            their names they had in the zip archive.
    """
    url = url.split('#')[0]  # If the album ends with an image index like /a/0ga2f#0, remove it
    response = requests.get("{}/zip".format(url))
    with tempfile.TemporaryFile(mode="w+b") as file:
        file.write(response.content)
        file.seek(0)
        zipfile = ZipFile(file)
        if file_name == "":
            zipfile.extractall(path)
        else:
            tempdir = tempfile.mkdtemp()
            zipfile.extractall(tempdir)
            for i, image in enumerate(os.listdir(tempdir)):
                extension = image.split('.')[-1]
                shutil.copyfile("{}/{}".format(tempdir, image),
                                "{}/{}.{}.{}".format(path, file_name, i + 1, extension))
                # /home/user/images/myimg.1.png


def imgur_link(url, path, file_name=""):
    """Download the image from imgur link.

    Args:
        url: A url to an imgur image.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.
    """
    download_name = url.split('/')[-1]
    # The file extension doesn't have to be a .jpg,
    # Imgur returns the image as long as it is requested with a known file extension.
    # download function will correct the extension based on the headers.
    download("https://i.imgur.com/{}.jpg".format(download_name), path, file_name)


def tumblr_link(url, path, file_name=""):
    """Download the image from a tumblr post.

    This function assumes that there is only a single image in the tumblr post.
    If the tumblr supports multiple images per post, only first will be downloaded.

    Args:
        url: A url to a tumblr post.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    post_content = soup(attrs={"class": "post-content"})
    image = BeautifulSoup(str(post_content)).find("img")
    download(image["src"], path, file_name)


def manage_download(url, path, file_name=""):
    """Decide on the function to download the image and handle errors.

    The function should not raise any errors unless it is critical.
    Failure to download the image or find a suitable method will only
    make the function return False.

    To make new websites available, simply add them

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
        if is_direct_image(url):
            download(url, path, file_name)
        elif "imgur.com/a" in url:
            imgur_album(url, path, file_name)
        elif "imgur.com/" in url:
            imgur_link(url, path, file_name)
        elif "tumblr.com/post/" in url:
            tumblr_link(url, path, file_name)
        else:  # Unrecognised website/file
            return url, False
        return url, True
    except (OSError, IOError, AttributeError, IndexError):
        return url, False


def download_submissions(submission_list, path, processes, use_titles=True):
    """Download all images in the submission_list to path.

    Args:
        submission_list: An iterable, containing praw.objects.Submission objects,
            or any other object that has .url and .title attributes.
        path: Path to the folder where images should be saved.
        processes: Number of processes to use for searching and downloading.
        use_titles: If set to True, titles of the submissions will be used
            as file names for the downloaded images.
    """
    download_queue = []
    if use_titles:
        for sub in submission_list:
            if isinstance(sub, praw.objects.Submission):
                if use_titles:
                    download_queue.append((sub.url, path, sub.title))
                else:
                    download_queue.append((sub.url, path, ""))
    if processes > 1:
        with multiprocessing.Pool(processes=processes) as pool:
            results = pool.starmap(manage_download, download_queue)
    else:
        results = [manage_download(*submission) for submission in download_queue]
    return results


def __main():
    parser = argparse.ArgumentParser(description="Downloads your saved images from Reddit.")
    parser.add_argument("-u", "--username", type=str, required=True,
                        help="Reddit username.")
    parser.add_argument("-p", "--password", type=str, required=True,
                        help="Reddit password.")
    parser.add_argument("-d", "--savedir", type=str, required=True,
                        help="Directory to save the images.")
    parser.add_argument("-c", "--processes", type=int, default=5,
                        help="Number of processes to use. "
                             "Use 1 to disable multiprocessing.")
    parser.add_argument("-n", "--notitles", action="store_true", default=False,
                        help="Do not use titles of submissions as file names, "
                             "use the names of downloaded files instead.")
    parser.add_argument("-r", "--remove", action="store_true", default=False,
                        help="Remove the files that were successfully downloaded from saved.")
    parser.add_argument("-s", "--silent", action="store_true", default=False,
                        help="Do not print anything about the scripts actions.")
    args = parser.parse_args()
    if args.silent:
        prints = lambda x: None
    else:
        prints = print

    r = praw.Reddit(user_agent="Just {} downloading some images".format(args.username))
    prints("Logging in as {}.".format(args.username))
    r.login(username=args.username, password=args.password)
    prints("Logged in.")
    prints("Getting data...")
    saved = r.user.get_saved(limit=None)
    prints("Starting to download, using {} processes.".format(args.processes))
    downloaded = download_submissions(saved, args.savedir, args.processes, not args.notitles)
    prints("Processed {} urls.".format(len(downloaded)))
    success_count = 0
    fail_count = 0
    for i, submission in enumerate(downloaded):
        url, successful = submission
        if not successful:
            fail_count += 1
            prints("Download failed: {}".format(url))
        else:  # successful
            success_count += 1
            if args.remove:
                saved[i].unsave()
    prints("\nDownloading finished.")
    prints("Successful: {} \t Failed: {}".format(success_count, fail_count))

if __name__ == "__main__":
    __main()