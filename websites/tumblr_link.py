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
from . import direct
import re

match = re.compile("imgur.com/[\S]+").search


def download(url, path, file_name=""):
    """Download the image from a tumblr post.

    Args:
        url: A url to a tumblr post.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    post_content = soup(attrs={"class": "post-content"})
    images = BeautifulSoup(str(post_content)).findAll("img")
    if len(images) == 1:
        direct.download(images[0]["src"], path, file_name)
    else:
        for i, image in enumerate(images):
            direct.download(images["src"], path, "{}.{}".format(file_name, i))
