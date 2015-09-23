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
import json
import re
from redditcurl.websites import direct
from redditcurl.websites import shared_config

_GFYCAT_API_URL = "https://gfycat.com/cajax/get/{}"

match = re.compile("^https?://(www[.])?gfycat.com/[a-zA-Z]+[?#]*$").search


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
    image_name = url.split("/")[-1]
    api_request = requests.get(_GFYCAT_API_URL.format(image_name))
    api_data = json.loads(api_request.content.decode("utf-8"))
    if shared_config.PREFER_MP4:
        file_type = "mp4Url"
    else:
        file_type = "webmUrl"
    direct.download(api_data["gfyItem"][file_type], path, file_name)
