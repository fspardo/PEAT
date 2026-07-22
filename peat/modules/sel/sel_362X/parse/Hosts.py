"""
Parse data from /Hosts.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse the page
    """
    result = {}

    table = soup.find("table", {"id": "HostnameTable"})
    if not isinstance(table, Tag):
        raise Exception("Table not found")

    rows = table.find_all("tr", {"class": ["even", "odd"]})

    for row in rows:
        assert isinstance(row, Tag)
        name = row.find("td", {"class": "hostname"})
        assert isinstance(name, Tag)
        address = row.find("td", {"class": "ip_address"})
        assert isinstance(address, Tag)

        result[name.get_text(strip=True)] = address.get_text(strip=True)
    return result
