import os
import platform
from typing import Any
from urllib.request import getproxies

from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from hentai.consts import __version__, package_name


def _build_ua_string() -> str:
    """
    Return a descriptive and truthful user agent string.
    """
    user_name: str = os.environ.get(
        "USERNAME" if platform.system() == "Windows" else "USER", "N/A"
    )
    return (
        f"{package_name}/{__version__} {platform.system()}/"
        f"{platform.release()} CPython/{platform.python_version()} "
        f"user_name/{user_name}"
    )


class RequestHandler(object):
    """
    RequestHandler
    ==============
    Defines a synchronous request handler class that provides methods and
    properties for working with REST APIs that is backed by the `requests`
    library.

    Example
    -------
    ```
    from hentai import Hentai, RequestHandler

    response = RequestHandler().get(url=Hentai.HOME)

    # True
    print(response.ok)
    ```
    """

    __slots__: list[str] = [
        "timeout",
        "total",
        "status_forcelist",
        "backoff_factor",
        "user_agent",
        "proxies",
    ]

    _timeout: tuple[float, float] = (5, 5)
    _total = 5
    _status_forcelist: list[int] = [413, 429, 500, 502, 503, 504]
    _backoff_factor = 1
    _user_agent: str = ""
    _proxies: dict[str, str] = {}

    def __init__(
        self,
        timeout: tuple[float, float] = _timeout,
        total: int = _total,
        status_forcelist: list[int] = _status_forcelist,
        backoff_factor: int = _backoff_factor,
        user_agent: str = _user_agent,
        proxies: dict[str, str] = _proxies,
    ) -> None:
        """
        Instantiates a new request handler object.
        """
        self.timeout: tuple[float, float] = timeout
        self.total: int = total
        self.status_forcelist: list[int] = status_forcelist
        self.backoff_factor: int = backoff_factor
        self.user_agent: str = user_agent
        self.proxies: dict[str, str] = proxies

    @property
    def retry_strategy(self) -> Retry:
        """
        The retry strategy returns the retry configuration made up of the
        number of total retries, the status forcelist as well as the backoff
        factor. It is used in the session property where these values are
        passed to the HTTPAdapter.
        """
        return Retry(
            total=self.total,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
        )

    @property
    def session(self) -> Session:
        """
        Creates a custom session object. A request session provides cookie
        persistence, connection-pooling, and further configuration options
        that are exposed in the RequestHandler methods in form of parameters
        and keyword arguments.
        """

        def _hook_response(response: Response, *args: Any, **kwargs: Any) -> None:
            """
            Hook to raise an HTTPError if the response was unsuccessful.
            """
            response.raise_for_status()

        session = Session()
        session.mount("https://", HTTPAdapter(max_retries=self.retry_strategy))
        session.hooks["response"] = [_hook_response]
        session.headers.update({"User-Agent": self.user_agent or _build_ua_string()})
        return session

    def get(self, url: str, **kwargs: Any) -> Response:
        """
        Returns the GET request encoded in `utf-8`. Adds proxies to this session
        on the fly if urllib is able to pick up the system's proxy settings.
        """
        response = self.session.get(
            url, timeout=self.timeout, proxies=self.proxies or getproxies(), **kwargs
        )
        response.encoding = "utf-8"
        return response
