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

    table = soup.find("table", {"id": "SharedClients"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["even", "odd"]})

    for row in rows:
        assert isinstance(row, Tag)

        alias = row.find("td", {"class": "Alias"})
        assert isinstance(alias, Tag)
        alias = alias.get_text("", True)

        address = row.find("td", {"class": "IP"})
        assert isinstance(address, Tag)
        address = address.get_text("", True)

        description = row.find("td", {"class": "Description"})
        assert isinstance(description, Tag)
        description = description.get_text("", True)

        types = row.find("td", {"class": "Types"})
        assert isinstance(types, Tag)
        imgs = types.find_all("img")
        types = types.get_text(";").split(";")

        result[alias] = {
            "address": address,
            "description": description,
            "types": [t.strip("\u00a0") for t in types],
        }

    return result
