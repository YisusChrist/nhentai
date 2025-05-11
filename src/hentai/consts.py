import errno
import os
from urllib.parse import urljoin

COLORS: dict[str, str] = {
    "reset": "\033[0m",
    "bright": "\033[1m",
    "dim": "\033[2m",
    "normal": "",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

__version__ = "3.2.10"
package_name = "nhentai"
python_major = "3"
python_minor = "7"

HOME_URL = "https://nhentai.net/"
GALLERY_URL: str = urljoin(HOME_URL, "/g/")
API_URL: str = urljoin(HOME_URL, "/api/gallery/")

ERROR_VALUE: str = os.strerror(errno.EINVAL)
