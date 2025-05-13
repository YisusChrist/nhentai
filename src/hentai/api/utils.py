"""
Hentai Utility Library
======================
This class provides a handful of miscellaneous static methods that extend the
functionality of the `Hentai` class.

Example 1
---------
```
from hentai.utils import get_random_id

# 177013
print(get_random_id())
```

Example 2
---------
```
from hentai import Sort
from hentai.utils import search_by_query

lolis = search_by_query('tag:loli', sort=Sort.PopularWeek)
```
"""

import functools
import json
import platform
import sys
import tarfile
from pathlib import Path
from random import randint
from typing import TYPE_CHECKING, Any, Callable, Optional, Union
from urllib.parse import urljoin, urlparse
from zipfile import ZIP_DEFLATED, ZipFile

from requests import HTTPError, Response
from rich import print

from hentai.api.models import Option
from hentai.consts import HOME_URL
from hentai.logs import logger
from hentai.requests import RequestHandler

if TYPE_CHECKING:
    from hentai.api.hentai import Hentai


def exists(error_msg: bool = False) -> Callable[..., Callable[[Any], Any]]:
    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any | None:
            try:
                return func(*args, **kwargs)
            except HTTPError as error:
                logger.error(
                    f"DNE (*args={','.join([arg for arg in args])})", exc_info=True
                )
                if error_msg:
                    print(error, file=sys.stderr)

        return wrapper

    return decorator


def get_random_id(handler: RequestHandler = RequestHandler()) -> int:
    """
    Return a random ID.
    """
    response: Response = handler.get(urljoin(HOME_URL, "random"))
    return int(urlparse(response.url).path.split("/")[-2])


def get_random_hentai(handler: RequestHandler = RequestHandler()) -> "Hentai":
    """
    Return a random `Hentai` object.
    """
    from hentai.api.hentai import Hentai

    return Hentai(get_random_id(handler))


def get_random_cdn() -> int:
    """
    Return a random CDN ID.
    """
    return randint(1, 4)


def download(
    doujins: list["Hentai"],
    delay: float = 0,
    progressbar: bool = False,
    zip_dir: bool = False,
) -> None:
    """
    Download all image URLs for a sequence of `Hentai` object to the CWD,
    excluding cover and thumbnail. set a `delay` between each image download
    in seconds. Enable `progressbar` for status feedback in terminal applications.
    """
    for doujin in doujins:
        doujin.download(delay=delay, progressbar=progressbar, zip_dir=zip_dir)


def export(
    iterable: list["Hentai"],
    filename: Union[str, Path],
    options: Optional[list[Option]] = None,
) -> None:
    """
    Store user-customized data of `Hentai` objects as a JSON file.
    Includes all available options by default.

    Example
    -------
    ```
    from hentai.utils import export, search_by_query
    from hentai import Sort, Option

    lolis = search_by_query('tag:loli', sort=Sort.PopularToday)
    export(popular_loli, Path('lolis.json'), options=[Option.ID, Option.Title])
    ```
    """
    if options is None:
        export(iterable, filename, options=Option.all())
    elif Option.Raw in options:
        with open(filename, mode="w", encoding="utf-8") as file_handler:
            json.dump([doujin.json for doujin in iterable], file_handler)
    else:
        with open(filename, mode="w", encoding="utf-8") as file_handler:
            json.dump([doujin.dictionary(options) for doujin in iterable], file_handler)


def compress(folder: Union[str, Path]) -> None:
    """
    Archive `folder` as `ZipFile` (Windows) or `TarFile` (Linux and macOS)
    using the highest compression levels available.
    """
    if platform.system() == "Windows":
        with ZipFile(
            f"{str(folder)}.zip",
            mode="w",
            compression=ZIP_DEFLATED,
            compresslevel=9,
        ) as zip_handler:
            for file in Path(folder).glob("**/*"):
                zip_handler.write(file)
    else:
        with tarfile.open(f"{str(folder)}.tar.gz", mode="x:gz") as tar_handler:
            tar_handler.add(str(folder))
