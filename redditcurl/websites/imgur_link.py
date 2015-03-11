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
from redditcurl.websites import direct
import re

match = re.compile("imgur.com/[\S]+").search


def download(url, path, file_name=""):
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
    direct.download("https://i.imgur.com/{}.jpg".format(download_name), path, file_name)
