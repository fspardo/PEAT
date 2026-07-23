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

from .helper import *


def parse_clients(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    table = find_table(soup, {"id": "SharedClients"})
    rows = get_table_rows(table)

    for row in rows:
        alias = get_text_of(row, "td", {"class": "Alias"})
        address = get_text_of(row, "td", {"class": "IP"})
        description = get_text_of(row, "td", {"class": "Description"})

        types = find_tag_f(row, "td", {"class": "Types"})

        imgs = find_tags(types, "img")
        types = types.get_text(";", True).split(";")

        result[alias] = {
            "address": address,
            "description": description,
            "types": [
                types[i].strip("\u00a0")
                for i in range(len(types))
                if imgs[i].get("src") in ["/images/checked.JPG"]
            ],
        }

    return result
