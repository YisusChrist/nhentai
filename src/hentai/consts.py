import errno
import os
from urllib.parse import urljoin

__version__ = "3.2.10"
package_name = "nhentai"
python_major = "3"
python_minor = "7"

GREEN = "\033[32m"
RESET = "\033[0m"

HOME_URL = "https://nhentai.net/"
GALLERY_URL: str = urljoin(HOME_URL, "/g/")
API_URL: str = urljoin(HOME_URL, "/api/gallery/")

ERROR_VALUE: str = os.strerror(errno.EINVAL)
