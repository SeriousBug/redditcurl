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
from redditcurl.websites import direct, gfycat, imgur_album, imgur_gifv, imgur_link, redditbooru_gallery, tumblr_link, deviantart
# Order is important to ensure the correct downloader gets picked
downloaders = [direct, gfycat, imgur_album, imgur_gifv, imgur_link, redditbooru_gallery, tumblr_link, deviantart]
