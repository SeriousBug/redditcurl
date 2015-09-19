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
from redditcurl.exceptions import DownloadError
import requests

_IMAGE_FORMATS = ['bmp', 'dib', 'eps', 'ps', 'gif', 'im', 'jpg', 'jpe', 'jpeg',
                  'pcd', 'pcx', 'png', 'pbm', 'pgm', 'ppm', 'psd', 'tif',
                  'tiff', 'xbm', 'xpm', 'rgb', 'rast', 'svg']


def match(url):
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
    if url.split('.')[-1] in _IMAGE_FORMATS:
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
    if not response.ok:
        raise DownloadError("Download of {} failed.".format(url))
    if file_name == "":
        base_name = url.split('/')[-1].split('.')[0]
    else:
        base_name = file_name
    if path == "":
        path = "."
    extension = response.headers["Content-Type"].split('/')[-1]
    with open("{}/{}.{}".format(path, base_name, extension), mode="wb") as file:
        file.write(response.content)
