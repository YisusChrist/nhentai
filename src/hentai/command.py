from argparse import Namespace
from pathlib import Path
from typing import NamedTuple

from rich import print

from hentai.api import Format, Hentai
from hentai.logs import get_logfile_path


class Entry(NamedTuple):
    """
    A data class that bundles related `Entry` properties.
    """

    timestamp: str
    levelname: str
    lineno: str
    name: str
    message: str


def str2bool(val: str) -> bool:
    """
    Convert string to boolean.
    """
    return val.lower() in ("", "y", "yes", "t", "true", "on", "1")


def __print_dict(dictionary: dict[str, str | int], indent: int = 4) -> None:
    print(
        "{\n%s\n}"
        % "\n".join(
            [
                f"[blue]{indent * ' '}{key}[/]: " f"[green]{value}[/],"
                for key, value in dictionary.items()
            ]
        )
    )


def __from_file(path: Path) -> list[int]:
    with open(path, mode="r", encoding="utf-8") as file_handler:
        return [int(line.strip("#").rstrip()) for line in file_handler.readlines()]


def download_doujin(args: Namespace):
    for id_ in args.id or __from_file(args.batch_file):
        doujin = Hentai(id_)
        if args.check and Path(args.dest).joinpath(str(doujin.id)).exists():
            print(
                f"[yellow]WARNING:[/] A file with the same name already exists in {str(args.dest)!r}."
            )
            choice = input("Proceed with download? [Y/n] ")
            if choice == "" or str2bool(choice):
                doujin.download(dest=args.dest, progressbar=args.verbose)
        else:
            doujin.download(dest=args.dest, progressbar=args.verbose)


def display_doujin_info(args: Namespace):
    for id_ in args.id:
        doujin = Hentai(id_)
        values: list[str | int] = [
            doujin.title(Format.Pretty),
            doujin.artist[0].name,
            doujin.num_pages,
            doujin.num_favorites,
            doujin.url,
        ]
        if args.verbose:
            __print_dict(
                dict(
                    zip(
                        ["Title", "Artist", "NumPages", "NumFavorites", "URL"],
                        values,
                    )
                )
            )
        else:
            print(",".join(map(str, values)))


def handle_log_file(args: Namespace):
    if args.reset:
        open(get_logfile_path(), mode="w", encoding="utf-8").close()
    if args.path:
        print(get_logfile_path())
    if args.list:
        with open(get_logfile_path(), mode="r", encoding="utf-8") as file_handler:
            log = file_handler.readlines()

            if not log:
                print(
                    f"[yellow]INFO:[/] There is nothing to read because the "
                    "log file is empty"
                )
                return

            def _parse_line(line: str) -> list[str]:
                return line.strip("\n").split("::")

            tabulate = "{:<24} {:<7} {:<8} {:<20} {:<30}".format
            print(
                f'[green]{tabulate("Timestamp", "Line", "Level", "File Name", "Message")}[/]'
            )

            for line in log:
                parsed_line = _parse_line(line)
                entry = Entry(
                    parsed_line[0],
                    parsed_line[1],
                    parsed_line[2],
                    parsed_line[3],
                    parsed_line[4],
                )
                print(
                    tabulate(
                        entry.timestamp,
                        entry.lineno.zfill(4),
                        entry.levelname,
                        entry.name,
                        entry.message,
                    )
                )
