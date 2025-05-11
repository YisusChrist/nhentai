from typing import Any, Iterable

from hentai.consts import COLORS


def progressbar_options(
    iterable: Iterable[Any],
    desc: str,
    unit: str,
    color: str = COLORS["green"],
    char: str = "\u25cb",
    disable: bool = False,
) -> dict[str, Any]:
    """
    Return custom optional arguments for `tqdm` progressbars.
    """
    return {
        "iterable": iterable,
        "bar_format": "{l_bar}%s{bar}%s{r_bar}" % (color, COLORS["reset"]),
        "ascii": char.rjust(9, " "),
        "desc": desc,
        "unit": unit.rjust(1, " "),
        "total": len(iterable),
        "disable": not disable,
    }
