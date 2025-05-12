from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, unique
from importlib.resources import path as resource_path
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union
from urllib.parse import urljoin, urlparse

from hentai.consts import COLORS, ERROR_VALUE, HOME_URL
from hentai.requests import RequestHandler

if TYPE_CHECKING:
    from hentai.api.hentai import Hentai


def _query_db(db: str, sql: str, *args: Any, local_: bool = False) -> list[Any]:
    """
    Apply a query to DBs that reside in the `hentai.data` namespace.
    """
    with resource_path(
        "src.hentai.data" if local_ else "hentai.data", db
    ) as resource_handler:
        with closing(sqlite3.connect(resource_handler)) as connection:
            with closing(connection.cursor()) as cursor:
                return cursor.execute(sql, *args).fetchall()


@dataclass(frozen=True)
class Homepage:
    """
    The `Homepage` dataclass contains all doujins from the frontpage of
    <https://nhentai.net>, which is divided into two sub-sections: the
    `popular_now` section features 5 trending doujins, while `new_uploads`
    returns the 25 most recent additions to the DB.
    """

    popular_now: set["Hentai"]
    new_uploads: set["Hentai"]


@dataclass(frozen=True)
class User:
    """
    Provides public account information.
    """

    id: int
    username: str
    slug: str
    avatar_url: str
    is_superuser: bool
    is_staff: bool

    @property
    def url(self) -> str:
        return urljoin(HOME_URL, f"/users/{self.id}/{self.slug}")


@dataclass(frozen=True)
class Comment:
    """
    Defines comment object instances of doujin threads.
    """

    id: int
    gallery_id: int
    poster: User
    post_date: datetime
    body: str


@dataclass(frozen=True)
class Tag:
    """
    A data class that bundles related `Tag` properties and useful helper methods
    for interacting with tags.
    """

    id: int
    type: str
    name: str
    url: str
    count: int

    @classmethod
    def get(cls, tags: list[Tag], property_: str) -> str:
        """
        Return a list of tags as comma-separated string.

        Example
        -------
        ```
        from hentai import Hentai, Tag

        doujin = Hentai(177013)

        # english, translated
        print(Tag.get(doujin.language, 'name'))
        ```
        """
        if property_ not in Tag.__dict__.get("__dataclass_fields__").keys():
            raise ValueError(
                f"{COLORS['red']}{ERROR_VALUE}: {property_} not recognized as a property in {cls.__name__}{COLORS['reset']}"
            )
        return ", ".join([getattr(tag, property_) for tag in tags])

    @staticmethod
    def list(option: Option, local_: bool = False) -> list[Tag]:
        """
        Return a list of all tags where `option` is either

        `Option.Artist`
        `Option.Character`
        `Option.Group`
        `Option.Parody`
        `Option.Tag`
        `Option.Language`

        Example
        -------
        ```
        from hentai import Tag, Option

        # ['009-1', '07-ghost', '08th ms team', ...]
        print([tag.name for tag in Tag.list(Option.Group)])
        ```

        Note
        ----
        All tag count properties whose values exceed 999 are rounded to the nearest thousand.
        """
        if option not in [
            Option.Artist,
            Option.Character,
            Option.Group,
            Option.Parody,
            Option.Tag,
            Option.Language,
            Option.Category,
        ]:
            raise ValueError(
                f"{COLORS['red']}{ERROR_VALUE}: Invalid option ({option.name} is not an Tag object property){COLORS['reset']}"
            )

        if option is Option.Category:
            raise NotImplementedError(
                f"{COLORS['red']}This feature is not implemented yet{COLORS['reset']}"
            )

        tags = _query_db(
            "tags.db",
            "SELECT * FROM Tag WHERE Type=:type_",
            {"type_": option.value},
            local_=local_,
        )
        number = lambda count: (
            int(count) if str(count).isnumeric() else int(count.strip("K")) * 1_000
        )
        return [
            Tag(int(tag[0]), tag[1], tag[2], urljoin(HOME_URL, tag[3]), number(tag[4]))
            for tag in tags
        ]

    @staticmethod
    def search(option: Option, property_: str, value: str, local_: bool = False) -> Tag:
        """
        Return the first tag object of type `option` whose `property_` matches with `value`.

        Example
        -------
        ```
        from hentai import Tag

        # ID=3981
        print(f"ID={Tag.search(Option.Artist, 'name', 'shindol').id}")
        ```
        """
        return next(
            filter(  # type: ignore
                lambda tag: getattr(tag, property_) == value,
                Tag.list(option, local_=local_),
            ),
            None,
        )


@dataclass(frozen=True)
class Page:
    """
    A data class that bundles related `Page` properties.
    """

    url: str
    ext: str
    width: int
    height: int

    @property
    def filename(self) -> Path:
        """
        Return the file name for this `Page` as Path object.

        Example
        -------
        ```
        from hentai import Hentai

        doujin = Hentai(177013)

        # [WindowsPath('1.jpg'), WindowsPath('2.jpg'), ...]
        print([page.filename for page in doujin.pages])
        ```
        """
        num = Path(urlparse(self.url).path).name
        return Path(num).with_suffix(self.ext)

    def download(
        self, handler: RequestHandler, dest: Union[str, Path] = Path.cwd()
    ) -> None:
        """
        Download an individual page to `dest`.

        Example
        -------
        ```
        from hentai import Hentai

        doujin = Hentai(177013)

        # download the last page to the CWD
        doujin.pages[-1].download(doujin.handler)
        ```
        """
        with open(Path(dest).joinpath(self.filename), mode="wb") as file_handler:
            for chunk in handler.get(self.url, stream=True).iter_content(1024 * 1024):
                file_handler.write(chunk)


@unique
class Sort(Enum):
    """
    Expose endpoints used to sort queries. Defaults to `Popular`.
    """

    Popular = "popular"
    PopularMonth = "popular-month"
    PopularWeek = "popular-week"
    PopularToday = "popular-today"
    Date = "date"


@unique
class Option(Enum):
    """
    Define export options for the `Hentai` and `Utils` class.
    """

    Raw = "raw"
    ID = "id"
    Title = "title"
    Scanlator = "scanlator"
    URL = "url"
    API = "api"
    MediaID = "media_id"
    Epos = "epos"
    NumFavorites = "num_favorites"
    Tag = "tag"
    Group = "group"
    Parody = "parody"
    Character = "character"
    Language = "language"
    Artist = "artist"
    Category = "category"
    Cover = "cover"
    Thumbnail = "thumbnail"
    Images = "image_urls"
    NumPages = "num_pages"

    def all() -> list[Option]:
        """
        Return all available options with the exception of `Option.Raw`.
        """
        return [option for option in Option if option.value != "raw"]


@unique
class Format(Enum):
    """
    The title format. In some instances, `Format.Japanese` or `Format.Pretty`
    return an empty string.
    """

    English = "english"
    Japanese = "japanese"
    Pretty = "pretty"


@unique
class Extension(Enum):
    """
    Known file extensions used by `nhentai` images.
    """

    JPG = "j"
    PNG = "p"
    GIF = "g"
    WEBP = "w"

    @classmethod
    def convert(cls, key: str) -> str:
        """
        Convert Extension enum to its string representation.

        Example
        -------
        ```
        from hentai import Extension

        # .jpg
        print(Extension.convert('j'))
        ```
        """
        return f".{cls(key).name.lower()}"
