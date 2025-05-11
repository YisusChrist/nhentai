import argparse
import sys
from pathlib import Path

from hentai import __version__, package_name

parser = None


def get_parsed_args() -> argparse.Namespace:
    global parser

    formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=52)
    parser = argparse.ArgumentParser(
        prog=package_name,
        formatter_class=formatter,
        description="hentai command line interface.",
    )
    parser._positionals.title = "Commands"
    parser._optionals.title = "Arguments"

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-V",
        "--verbose",
        default=True,
        action="store_true",
        help="increase output verbosity (default: %(default)s)",
    )
    parser.add_argument(
        "--no-verbose",
        dest="verbose",
        action="store_false",
        help="run commands silently",
    )
    parser.add_argument(
        "-a",
        "--user-agent",
        type=str,
        default=None,
        help="configure custom User-Agent (optional)",
    )
    parser.add_argument(
        "-p",
        "--proxies",
        type=str,
        default=None,
        help="configure HTTP and/or HTTPS proxies (optional)",
    )

    subparser = parser.add_subparsers(dest="command")

    download_help_msg = (
        "download a doujin from https://nhentai.net/ to your local harddrive"
    )
    download_parser = subparser.add_parser(
        "download", description=download_help_msg, help=download_help_msg
    )
    download_parser.add_argument("--id", type=int, nargs="*", help="doujin ID")
    download_parser.add_argument(
        "--dest",
        type=Path,
        metavar="PATH",
        default=Path.cwd(),
        help="download directory (default: %(default)s)",
    )
    download_parser.add_argument(
        "-c",
        "--check",
        default=True,
        action="store_true",
        help="check for duplicates (default: %(default)s)",
    )
    download_parser.add_argument(
        "--no-check",
        dest="check",
        action="store_false",
        help="disable checking for duplicates",
    )
    download_parser.add_argument(
        "--batch-file",
        type=Path,
        metavar="PATH",
        nargs="?",
        help="file containing IDs to download, one ID per line",
    )

    preview_help_msg = "print doujin meta data"
    preview_parser = subparser.add_parser(
        "preview", description=preview_help_msg, help=preview_help_msg
    )
    preview_parser.add_argument(
        "--id", type=int, nargs="+", required=True, help="doujin ID"
    )

    log_help_msg = "access the CLI logger"
    log_parser = subparser.add_parser(
        "log", description=log_help_msg, help=log_help_msg
    )
    log_parser.add_argument(
        "--reset", action="store_true", help="reset all log file entries"
    )
    log_parser.add_argument(
        "--path", action="store_true", help="return the log file path"
    )
    log_parser.add_argument("--list", action="store_true", help="read the log file")

    return parser.parse_args()


def print_help() -> None:
    """
    Print the help message for the CLI.
    """
    if parser:
        parser.print_help(sys.stderr)
