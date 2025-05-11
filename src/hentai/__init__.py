#!/usr/bin/env python3

from __future__ import annotations

import sys

from hentai.consts import __version__, package_name, python_major, python_minor

try:
    assert sys.version_info >= (int(python_major), int(python_minor))
except AssertionError:
    raise RuntimeError(
        f"\033[31m{package_name!r} requires Python {python_major}."
        f"{python_minor}+ (You have Python {sys.version})\033[0m"
    )


from hentai.command import (display_doujin_info, download_doujin,
                            handle_log_file)
from hentai.consts import API_URL, GALLERY_URL, HOME_URL
from hentai.api import *
from hentai.logs import *
