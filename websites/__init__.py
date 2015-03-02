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
import os
import importlib

__importpath__ = os.path.dirname(os.path.realpath(__file__))
__all__ = [file[:-3] for file in os.listdir(__importpath__) if file[-3:] == ".py" and not file[:2] == "__"]

for module in __all__:
    try:
        importlib.import_module(".{}".format(module), "websites")
    except ImportError:
        __all__.remove(module)
        print("Unable to load module {}.".format(module))