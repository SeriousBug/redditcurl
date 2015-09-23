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
from redditcurl.websites import direct
from redditcurl.websites import shared_config

match = re.compile("imgur.com/[\S]+[.]gifv").search


def download(url, path, file_name=""):
    """Download an imgur gifv video.

    Args:
        url: A url to an imgur gifv.
        path: Path to the folder where the image should be saved.
        file_name: File name to use when saving the image.
            If file_name is an empty string, name of the downloaded file will be used.
    """
    # From an url "http://i.imgur.com/abcdef.gifv", first extract "abcdef.gifv" then
    # delete the extension to get "abcdef"
    download_name = url.split('/')[-1][:-5]
    if shared_config.PREFER_MP4:
        extension = "mp4"
    else:
        extension = "webm"
    direct.download("https://i.imgur.com/{}.{}".format(download_name, extension), path, file_name)
