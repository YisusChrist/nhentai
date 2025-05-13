import html
import re
import sys
from urllib.parse import urljoin

from requests import HTTPError
from rich import print
from tqdm import tqdm

from hentai.api.hentai import Hentai
from hentai.api.models import Homepage, Sort
from hentai.api.progress import progressbar_options
from hentai.api.search import search_by_query
from hentai.consts import ERROR_VALUE, HOME_URL
from hentai.logs import logger
from hentai.requests import RequestHandler


def browse_homepage(
    start_page: int,
    end_page: int,
    handler: RequestHandler = RequestHandler(),
    progressbar: bool = False,
) -> set[Hentai]:
    """
    Return a list of `Hentai` objects that are currently featured on the homepage
    in range of `[start_page, end_page]`. Each page contains as much as 25 results.
    Enable `progressbar` for status feedback in terminal applications.
    """
    if start_page > end_page:
        raise ValueError(
            f"{ERROR_VALUE}: start_page={start_page} <= {end_page}=end_page "
            "is False"
        )
    data: set[Hentai] = set()
    for page in tqdm(
        **progressbar_options(
            range(start_page, end_page + 1), "Browse", "page", disable=progressbar
        )
    ):
        with handler.get(
            urljoin(HOME_URL, "api/galleries/all"), params={"page": page}
        ) as response:
            for raw_json in response.json()["result"]:
                data.add(Hentai(json=raw_json))
    return data


def get_homepage(handler: RequestHandler = RequestHandler()) -> Homepage | None:
    """
    Return an `Homepage` object, i.e. all doujins from the first page of the
    homepage.

    Example
    -------
    ```
    from hentai.utils import get_homepage

    homepage = get_homepage()
    popular_now = homepage.popular_now
    new_uploads = homepage.new_uploads
    ```
    """
    try:
        html_ = html.unescape(handler.get(HOME_URL).text)
    except HTTPError as error:
        logger.error(
            f"Failed to establish a connection to {HOME_URL}", exc_info=True
        )
        print(error, file=sys.stderr)
    else:
        titles = re.findall(r"""<div class="caption">(.*?)</div>""", html_, re.I)[0:5]

        return Homepage(
            popular_now={
                doujin
                for doujin in search_by_query(
                    query="*", sort=Sort.PopularToday, handler=handler
                )
                if str(doujin) in titles
            },
            new_uploads=browse_homepage(1, 1, handler),
        )
