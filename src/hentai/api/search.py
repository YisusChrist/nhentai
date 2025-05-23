from urllib.parse import urljoin

from tqdm import tqdm

from hentai.api.hentai import Hentai
from hentai.api.models import Sort
from hentai.api.progress import progressbar_options
from hentai.consts import HOME_URL
from hentai.requests import RequestHandler


def _search(
    endpoint: str,
    payload: dict[str, str | int],
    handler: RequestHandler,
) -> set[Hentai]:
    """
    Internal helper to search hentai data from a given API endpoint with payload.
    """
    with handler.get(urljoin(HOME_URL, endpoint), params=payload) as response:
        return {Hentai(json=raw_json) for raw_json in response.json()["result"]}


def search_by_query(
    query: str,
    page: int = 1,
    sort: Sort = Sort.Popular,
    handler: RequestHandler = RequestHandler(),
) -> set[Hentai]:
    """
    Return a list of `Hentai` objects on page `page` that match this search
    `query` sorted by `sort`.
    """
    payload: dict[str, str | int] = {"query": query, "page": page, "sort": sort.value}
    return _search("api/galleries/search", payload, handler)


def search_by_tag(
    id_: int,
    page: int = 1,
    sort: Sort = Sort.Popular,
    handler: RequestHandler = RequestHandler(),
) -> set[Hentai]:
    """
    Return a list of `Hentai` objects on page `page` that match this tag
    `id_` sorted by `sort`.
    """
    payload: dict[str, str | int] = {"tag_id": id_, "page": page, "sort": sort.value}
    return _search("api/galleries/tagged", payload, handler)


def search_all_by_query(
    query: str,
    sort: Sort = Sort.Popular,
    handler: RequestHandler = RequestHandler(),
    progressbar: bool = False,
) -> set[Hentai]:
    """
    Return a list of all `Hentai` objects that match this search `query`
    sorted by `sort`. Enable `progressbar` for status feedback in terminal applications.

    Example
    -------
    ```
    from hentai.utils import search_all_by_query
    from hentai import Sort

    lolis = search_all_by_query('tag:loli', sort=Sort.PopularToday)
    ```
    """
    data: set[Hentai] = set()
    payload: dict[str, str | int] = {"query": query, "page": 1, "sort": sort.value}
    endpoint = "api/galleries/search"

    with handler.get(urljoin(HOME_URL, endpoint), params=payload) as response:
        total_pages: int = int(response.json()["num_pages"]) + 1

    for page in tqdm(
        **progressbar_options(
            range(1, total_pages),
            "Search",
            "page",
            disable=progressbar,
        )
    ):
        data.update(search_by_query(query, page, sort, handler))

    return data
