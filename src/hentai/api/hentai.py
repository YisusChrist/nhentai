from __future__ import annotations

import html
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urljoin

from requests import HTTPError
from requests.models import Response
from tqdm import tqdm

from hentai.api.models import (Comment, Extension, Format, Option, Page, Tag,
                               User)
from hentai.api.progress import progressbar_options
from hentai.api.utils import compress, export, get_random_cdn
from hentai.consts import API_URL, COLORS, ERROR_VALUE, GALLERY_URL, HOME_URL
from hentai.logs import logger
from hentai.requests import RequestHandler


class Hentai(RequestHandler):
    """
    Python Hentai API Wrapper
    =========================
    Implements a wrapper class around `nhentai`'s RESTful API that inherits from
    `RequestHandler`. Note that the content of this module is generally considered
    NSFW.

    Basic Usage
    -----------
    ```
    from hentai import Hentai

    doujin = Hentai(177013)

    # [ShindoLA] METAMORPHOSIS (Complete) [English]
    print(doujin)
    ````

    Docs
    ----
    See full documentation at <https://www.hentai-chan.dev/projects/hentai>.
    """

    __slots__ = ["__id", "__handler", "__url", "__api", "__response", "__json"]

    def __init__(
        self,
        id_: int = 0,
        timeout: tuple[float, float] = RequestHandler._timeout,
        total: int = RequestHandler._total,
        status_forcelist: list[int] = RequestHandler._status_forcelist,
        backoff_factor: int = RequestHandler._backoff_factor,
        user_agent: str = RequestHandler._user_agent,
        proxies: dict[str, str] = RequestHandler._proxies,
        json: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Start a request session and parse meta data from <https://nhentai.net> for this `id`.
        """
        if id_ and not json:
            self.__id = id_
            super().__init__(
                timeout,
                total,
                status_forcelist,
                backoff_factor,
                user_agent,
                proxies,
            )
            self.__handler = RequestHandler(
                self.timeout,
                self.total,
                self.status_forcelist,
                self.backoff_factor,
                self.user_agent,
                self.proxies,
            )
            self.__url = urljoin(GALLERY_URL, str(self.id))
            self.__api = urljoin(API_URL, str(self.id))
            self.__response = self.handler.get(self.api)
            self.__json = self.response.json()
        elif not id_ and json:
            self.__json: dict[str, Any] = json
            self.__id = self.__get_id(self.json)
            self.__handler = RequestHandler()
            self.__url = self.__get_url(self.json)
            self.__api = self.__get_api(self.json)
        else:
            raise TypeError(
                f"{COLORS['red']}{ERROR_VALUE}: Define either id or json "
                f"as argument, but not both or none{COLORS['reset']}"
            )

    def __str__(self) -> str:
        return self.title()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ID={str(self.id).zfill(6)})"

    def __hash__(self) -> int:
        return hash(self.id)

    # region operators

    def __gt__(self, other: Hentai) -> bool:
        return self.id > other.id

    def __ge__(self, other: Hentai) -> bool:
        return self.id >= other.id

    def __eq__(self, other: Hentai) -> bool:
        return self.id == other.id

    def __le__(self, other: Hentai) -> bool:
        return self.id <= other.id

    def __lt__(self, other: Hentai) -> bool:
        return self.id < other.id

    def __ne__(self, other: Hentai) -> bool:
        return self.id != other.id

    # endregion

    # region private methods

    @staticmethod
    def __get_id(json: dict[str, Any]) -> int:
        """
        Return the ID of an raw nhentai response object.
        """
        return int(json["id"])

    @staticmethod
    def __get_url(json: dict[str, Any]) -> str:
        """
        Return the URL of an raw nhentai response object.
        """
        return urljoin(GALLERY_URL, str(Hentai.__get_id(json)))

    @staticmethod
    def __get_api(json: dict[str, Any]) -> str:
        """
        Return the API access point of an raw nhentai response object.
        """
        return urljoin(API_URL, str(Hentai.__get_id(json)))

    # endregion

    # region properties

    @property
    def id(self) -> int:
        """
        Return the ID of this `Hentai` object.
        """
        return self.__id

    @property
    def url(self) -> str:
        """
        Return the URL of this `Hentai` object.
        """
        return self.__url

    @property
    def api(self) -> str:
        """
        Return the API access point of this `Hentai` object.
        """
        return self.__api

    @property
    def json(self) -> dict[str, Any]:
        """
        Return the JSON content of this `Hentai` object.
        """
        return self.__json

    @property
    def handler(self) -> RequestHandler:
        """
        Return the `RequestHandler` of this `Hentai` object.
        """
        return self.__handler

    @property
    def response(self) -> Response:
        """
        Return the GET request response of this `Hentai` object.
        """
        return self.__response

    @property
    def media_id(self) -> int:
        """
        Return the media ID of this `Hentai` object.
        """
        return int(self.json["media_id"])

    def title(self, format_: Format = Format.English) -> str:
        """
        Return the title of this `Hentai` object. The format of the title
        defaults to `English`, which is the verbose counterpart to `Pretty`.
        """
        return self.json["title"].get(format_.value)

    @property
    def scanlator(self) -> str:
        """
        Return the scanlator of this `Hentai` object. This information is often
        not specified by the provider.
        """
        return self.json["scanlator"]

    @property
    def cover(self) -> str:
        """
        Return the cover URL of this `Hentai` object.
        """
        cover_ext = Extension.convert(self.json["images"]["cover"]["t"])
        cdn: int = get_random_cdn()
        return f"https://t{cdn}.nhentai.net/galleries/{self.media_id}/cover{cover_ext}"

    @property
    def thumbnail(self) -> str:
        """
        Return the thumbnail URL of this `Hentai` object.
        """
        thumb_ext = Extension.convert(self.json["images"]["thumbnail"]["t"])
        cdn: int = get_random_cdn()
        return f"https://t{cdn}.nhentai.net/galleries/{self.media_id}/thumb{thumb_ext}"

    @property
    def epos(self) -> int:
        """
        Return the epos of this `Hentai` object.
        """
        return self.json["upload_date"]

    @property
    def upload_date(self) -> datetime:
        """
        Return the upload date of this `Hentai` object as timezone aware datetime object.
        """
        return datetime.fromtimestamp(self.epos, tz=timezone.utc)

    def __tag(self, json_: dict[str, Any], type_: str) -> list[Tag]:
        return [
            Tag(
                tag["id"],
                tag["type"],
                tag["name"],
                urljoin(HOME_URL, tag["url"]),
                tag["count"],
            )
            for tag in json_["tags"]
            if tag["type"] == type_
        ]

    @property
    def tag(self) -> list[Tag]:
        """
        Return all tags of type tag of this `Hentai` object.
        """
        return self.__tag(self.json, "tag")

    @property
    def group(self) -> list[Tag]:
        """
        Return all tags of type group of this `Hentai` object. This tag is sometimes
        not specified by the provider.
        """
        return self.__tag(self.json, "group")

    @property
    def parody(self) -> list[Tag]:
        """
        Return all tags of type parody of this `Hentai` object. This tag is sometimes
        not specified by the provider.
        """
        return self.__tag(self.json, "parody")

    @property
    def character(self) -> list[Tag]:
        """
        Return all tags of type character of this `Hentai` object. This tag is sometimes
        not specified by the provider.
        """
        return self.__tag(self.json, "character")

    @property
    def language(self) -> list[Tag]:
        """
        Return all tags of type language of this `Hentai` object.
        """
        return self.__tag(self.json, "language")

    @property
    def artist(self) -> list[Tag]:
        """
        Return all tags of type artist of this `Hentai` object.
        """
        return self.__tag(self.json, "artist")

    @property
    def category(self) -> list[Tag]:
        """
        Return all tags of type category of this `Hentai` object.
        """
        return self.__tag(self.json, "category")

    @property
    def num_pages(self) -> int:
        """
        Return the total number of pages of this `Hentai` object.
        """
        return int(self.json["num_pages"])

    @property
    def num_favorites(self) -> int:
        """
        Return the number of times this `Hentai` object has been favorited. Because
        the API does not populate `num_favorites` of recently uploaded doujins,
        it will try to parse its HTML file as a fallback measure.
        """
        num_favorites = int(self.json["num_favorites"])

        if num_favorites == 0:
            try:
                html_ = html.unescape(self.handler.get(self.url).text)
                btn_content = re.findall(
                    r"""<span class="nobold">(.*?)</span>""", html_, re.I
                )
                num_favorites = int(btn_content[0].strip("()"))
            except HTTPError:
                logger.error(
                    f"An error occurred while trying to parse the HTML file for {repr(self)} (num_favorites={num_favorites})",
                    exc_info=True,
                )

        return num_favorites

    @property
    def pages(self) -> list[Page]:
        """
        Return a collection of pages detailing URL, file extension, width and
        height of this `Hentai` object.
        """
        pages: list[dict[str, Any]] = self.json["images"]["pages"]
        cdn: int = get_random_cdn()
        base_url: str = f"https://i{cdn}.nhentai.net/galleries/{self.media_id}"

        return [
            Page(
                f"{base_url}/{i + 1}{Extension.convert(pages[i]['t'])}",
                Extension.convert(p["t"]),
                p["w"],
                p["h"],
            )
            for i, p in enumerate(pages)
        ]

    @property
    def image_urls(self) -> list[str]:
        """
        Return all image URLs of this `Hentai` object, excluding cover and thumbnail.
        """
        return [image.url for image in self.pages]

    @property
    def related(self) -> set[Hentai]:
        """
        Return a set of five related doujins.
        """
        return {
            Hentai(json=raw_json)
            for raw_json in self.handler.get(
                urljoin(API_URL, f"{self.id}/related")
            ).json()["result"]
        }

    @property
    def thread(self) -> list[Comment]:
        """
        Return a list of comments of this `Hentai` object.
        """
        response: list[dict[str, Any]] = self.handler.get(
            urljoin(API_URL, f"{self.id}/comments")
        ).json()
        cdn: int = get_random_cdn()

        def to_user(u: dict[str, Any]) -> User:
            return User(
                int(u["id"]),
                u["username"],
                u["slug"],
                urljoin(f"https://i{cdn}.nhentai.net/", u["avatar_url"]),
                bool(u["is_superuser"]),
                bool(u["is_staff"]),
            )

        def to_comment(c: dict[str, Any]) -> Comment:
            return Comment(
                int(c["id"]),
                int(c["gallery_id"]),
                to_user(c["poster"]),
                datetime.fromtimestamp(c["post_date"], tz=timezone.utc),
                c["body"],
            )

        return [to_comment(c) for c in response]

    # endregion

    # region public methods

    def download(
        self,
        dest: Optional[Union[str, Path]] = None,
        folder: Optional[Union[str, Path]] = None,
        delay: float = 0,
        zip_dir: bool = False,
        progressbar: bool = False,
    ) -> None:
        """
        Download all image URLs of this `Hentai` object to `dest`, excluding cover
        and thumbnail. By default, `folder` will be located in the CWD named after
        the doujin's `id`. set a `delay` between each image download in seconds. If
        `zip_dir` is set to `True`, the download directory `folder` will be archived
        in `dest`. Enable `progressbar` for status feedback in terminal applications.
        """
        try:
            folder = str(self.id) if folder is None else str(folder)
            dest = Path(folder) if dest is None else Path(dest).joinpath(folder)
            dest.mkdir(parents=True, exist_ok=True)
            for page in tqdm(
                **progressbar_options(
                    self.pages,
                    f"Download #{str(self.id).zfill(6)}",
                    "page",
                    disable=progressbar,
                )
            ):
                page.download(self.handler, dest)
                time.sleep(delay)
            if zip_dir:
                compress(dest)
                shutil.rmtree(dest, ignore_errors=True)
        except HTTPError as error:
            logger.error(f"Download failed for {repr(self)}", exc_info=True)
            if progressbar:
                print(f"#{str(id).zfill(6)}: {error}", file=sys.stderr)

    def export(
        self, filename: Union[str, Path], options: Optional[list[Option]] = None
    ) -> None:
        """
        Store user-customized data about this `Hentai` object as a JSON file.
        Includes all available options by default.
        """
        export([self], filename, options)

    @staticmethod
    def exists(id_: int) -> bool:
        """
        Check whether or not an ID exists on <https://nhentai.net>.
        """
        try:
            return RequestHandler().get(urljoin(GALLERY_URL, str(id_))).ok
        except HTTPError:
            return False

    def dictionary(self, options: list[Option]) -> dict[str, Any]:
        """
        Return a dictionary for this `Hentai` object whose key-value pairs
        are determined by the `options` list.
        """
        data = {}

        if Option.Raw in options:
            raise NotImplementedError(
                f"{COLORS['red']}{ERROR_VALUE}: Access self.json to retrieve this information{COLORS['reset']}"
            )

        for option in options:
            property_ = getattr(self, option.value)
            if (
                isinstance(property_, list)
                and len(property_) != 0
                and isinstance(property_[0], Tag)
            ):
                data[option.value] = [tag.name for tag in property_]
            elif option.value == "title":
                data[option.value] = self.title(Format.Pretty)
            else:
                data[option.value] = property_

        return data

    # endregion
