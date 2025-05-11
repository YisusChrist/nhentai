from __future__ import annotations

import logging
import os
import platform
from pathlib import Path

from hentai.consts import package_name


def get_config_dir() -> Path:
    """
    Return a platform-specific root directory for user configuration settings.
    """
    return {
        "Windows": Path(os.path.expandvars("%LOCALAPPDATA%")),
        "Darwin": Path.home().joinpath("Library").joinpath("Application Support"),
        "Linux": Path.home().joinpath(".config"),
    }[platform.system()].joinpath(package_name)


def get_logfile_path() -> Path:
    """
    Return a platform-specific log file path.
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    log_file = config_dir.joinpath("error.log")
    log_file.touch(exist_ok=True)
    return log_file


logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
formatter = logging.Formatter(
    "%(asctime)s::%(levelname)s::%(lineno)d::%(name)s::%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler = logging.FileHandler(get_logfile_path())
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
