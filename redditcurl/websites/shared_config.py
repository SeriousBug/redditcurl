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
# This file holds variables used for configuration, that may be shared between packages.
# The values here are the defaults, and may be changed by the importer to pass the
# configuration to the downloaders.

PREFER_MP4 = False
# Used by gfycat and imgur_gifv, which by default downloaders will prefer WEBM.
# If PREFER_MP4 is set to True, they will prefer downloading MP4s instead.
