#!/usr/bin/env python3

"""
Implements a wrapper class around nhentai's RESTful API.
Copyright (C) 2020  hentai-chan (dev.hentai-chan@outlook.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import errno
import sys
from argparse import Namespace

from requests import HTTPError
from rich import print
from rich.traceback import install

from hentai.cli import get_parsed_args, print_help
from hentai.command import (display_doujin_info, download_doujin,
                            handle_log_file)
from hentai.consts import __version__
from hentai.logs import logger


def main() -> None:
    install()
    args: Namespace = get_parsed_args()

    try:
        if args.command == "download":
            download_doujin(args)
        elif args.command == "preview":
            display_doujin_info(args)
        elif args.command == "log":
            return handle_log_file(args)
        else:
            print_help()
            sys.exit(errno.EINVAL)
    except HTTPError as error:
        print(f"[red]ERROR:[/] {error}", file=sys.stderr)
        logger.error("CLI caught an HTTP error (network down?): %s" % str(error))
    except Exception as error:
        print(f"[red]ERROR:[/] {error}", file=sys.stderr)
        logger.error("CLI caught an error: %s" % str(error))


if __name__ == "__main__":
    main()
