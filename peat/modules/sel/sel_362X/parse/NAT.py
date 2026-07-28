"""
Parse data from /LocalGroups.sel.

Author: Francisco Santana
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_global_config(table: Tag | BeautifulSoup) -> dict[str, Any]:
    result = {}
    CELLS = {
        "status": "display_AddressTranslationStatus",
        "network_alias": "nat_NetworkAlias",
        "subnet": "nat_IpAddress",
    }

    for cell in CELLS:
        result[cell] = get_text_of(table, attrib={"id": CELLS[cell]})

    return result


def parse_nat_config(soup: BeautifulSoup) -> dict[str, Any]:
    result = parse_global_config(soup)

    return result
