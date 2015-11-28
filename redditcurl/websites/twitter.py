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
from bs4 import BeautifulSoup
import requests
import re
from redditcurl.websites import direct
from redditcurl.exceptions import DownloadError

_TWITTER_SEARCH_PROPERTY = "og:image"
_TWITTER_IMAGE_MATCH = re.compile("https?://pbs.twimg.com/media/").match


match = re.compile("^https?://twitter.com/[0-9a-zA-Z_]+/status/[0-9]+$").match


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
    request = requests.get(url)
    if not request.ok:
        raise DownloadError("Failed while getting data from Twitter for {}".format(url))
    soup = BeautifulSoup(request.content, "html.parser")
    # Twitter stores image link in meta property.
    image = soup.head.find("meta", property=_TWITTER_SEARCH_PROPERTY)["content"]
    # Ensure that we extracted the correct link
    if not _TWITTER_IMAGE_MATCH(image):
        raise DownloadError("Unable to locate image in Twitter post {}".format(url))
    direct.download(image, path, file_name)
