#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Håvard Moen <post@haavard.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
This file is part of gnome-search-lastpass.

gnome-search-lastpass is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

gnome-search-lastpass is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""

from pathlib import Path
from setuptools import setup
p = Path("icons")
icons = [('/usr/share/icons/hicolor/{}/apps/'.format(e.parts[1]), [str(e)]) for e in p.glob('*/*.png')]

setup(name="gnome-search-lastpass",
      version="1.0",
      description="Gnome shell lastpass search provider",
      author="Håvard Moen",
      author_email="post@haavard.name",
      url="https://github.com/umglurf/gnome-search-lastpass",
      license="GPL3",
      install_requires=["fuzzywuzzy", "python-Levenshtein", "PyGObject"],
      scripts=["lpass-search-provider.py", "lpass-show-copy.py"],
      data_files=[
          ("/usr/share/applications", ["name.haavard.Lastpass.desktop"]),
          ("/usr/share/gnome-shell/search-providers", ["name.haavard.Lastpass.SearchProvider.ini"]),
          ("/usr/share/dbus-1/services", ["name.haavard.Lastpass.SearchProvider.service"])
          ] + icons
      )
