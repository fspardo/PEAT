"""
Parse data from /AllowedClients.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_clients(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    return result
