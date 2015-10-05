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
import re


TUMBLR_API_URL = "https://api.tumblr.com/v2/blog/{domain}/posts?id={post_id}"
_TUMBLR_REGEXP = re.compile("^https?://([a-zA-Z0-9\-]+[.]tumblr[.]com)/post/([a-zA-Z0-9]+)")

match = _TUMBLR_REGEXP.search


def download(url, path, file_name=""):
    """Download the image from a tumblr post.

    Args:
        url: A url to a tumblr post.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.
    """
    domain, post_id = _TUMBLR_REGEXP.match(url).groups()
    api_request = requests.get(TUMBLR_API_URL.format(domain=domain, post_id=post_id))
    photos = api_request.json()["response"]["posts"][0]["photos"]
    for photo in photos:
        # Assuming that the first photo in alt_sizes is always the biggest
        direct.download(photo["alt_sizes"][0]["url"], path, file_name)
