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
import re
from redditcurl.exceptions import DownloadError
from redditcurl.websites import shared_config
import hashlib
import requests


match = re.compile(r"^https?://\S+[.]\S+/\S+[.](bmp|dib|eps|ps|gif|im|jpg|jpe|jpeg|pcd|pcx|png|pbm|pgm|ppm|psd|tif|tiff|xbm|xpm|rgb|rast|svg)(#\S*)?$").search


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
    if not response.ok:
        raise DownloadError("Download of {} failed.".format(url))
    if file_name == "":
        base_name = url.split('/')[-1].split('.')[0]
    else:
        base_name = file_name

    if shared_config.FILENAME_HASH:
        file_hash = ".{}".format(hashlib.md5(response.content).hexdigest()[:10])
    else:
        file_hash = ""

    if path == "":
        path = "."
    extension = response.headers["Content-Type"].split('/')[-1]
    with open("{}/{}{}.{}".format(path, base_name, file_hash, extension), mode="wb") as file:
        file.write(response.content)
