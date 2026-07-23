"""
Parse data from /Hosts.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse the page
    """
    result = {}

    table = find_table(soup, {"id": "HostnameTable"})
    rows = get_table_rows(table)

    for row in rows:
        name = get_text_of(row, "td", {"class": "hostname"})
        address = get_text_of(row, "td", {"class": "ip_address"})

        result[name] = address
    return result
