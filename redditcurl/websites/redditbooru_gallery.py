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
import requests
from bs4 import BeautifulSoup
from redditcurl.websites import direct
from redditcurl.exceptions import DownloadError
import re

match = re.compile("redditbooru.com/gallery/").search


def download(url, path, file_name=""):
    """Download the images from a RedditBooru gallery.

    Args:
        url: A url to a RedditBooru gallery.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the images.
            A number will be appended to the end of the name for
            each image in the album.
            If file_name is an empty string, the files will keep
            the names they have on the server.
    """
    response = requests.get(url)
    if not response.ok:
        raise DownloadError("Unable to download redditbooru gallery {}".format(url))
    soup = BeautifulSoup(response.content, "html.parser")
    images = soup.find_all("img")
    if len(images) < 1:
        raise DownloadError("Empty redditbooru gallery {}".format(url))
    if file_name == "":
        for image in images:
            direct.download(image["src"], path, file_name)
    else:
        for i, image in enumerate(images):
            direct.download(image["src"], path, "{}.{}".format(file_name, i + 1))
