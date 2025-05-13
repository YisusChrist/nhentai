from typing import Any, Sized

from hentai.consts import GREEN, RESET


def progressbar_options(
    iterable: Sized,
    desc: str,
    unit: str,
    color: str = GREEN,
    char: str = "\u25cb",
    disable: bool = False,
) -> dict[str, Any]:
    """
    Return custom optional arguments for `tqdm` progress bars.
    """
    return {
        "iterable": iterable,
        "bar_format": "{l_bar}%s{bar}%s{r_bar}" % (color, RESET),
        "ascii": char.rjust(9, " "),
        "desc": desc,
        "unit": unit.rjust(1, " "),
        "total": len(iterable),
        "disable": not disable,
    }
