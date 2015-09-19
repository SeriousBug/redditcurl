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
import tempfile
from zipfile import ZipFile
import shutil
import re
import os
from redditcurl.exceptions import DownloadError

match = re.compile("imgur.com/a/").search


def download(url, path, file_name=""):
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
    # If the album ends with an image index like /a/0ga2f#0, remove it
    url = url.split('#')[0]
    if path == "":
        path = "."
    response = requests.get("{}/zip".format(url))
    if not response.ok:
        raise DownloadError("Failed downloading imgur album {}".format(url))
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
