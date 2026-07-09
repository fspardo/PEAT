"""
Parse data from /PortMappings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_mappings(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    table = soup.find("table", {"id": "PortMappingGroups"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["odd", "oddProxy", "even", "evenProxy"]})
    # Convert into tuples; this makes parsing simpler.
    rows = [(rows[i], rows[i + 1]) for i in range(len(rows) // 2)]

    for name, conf in rows:
        # We need all of these to be tags.
        assert isinstance(name, Tag)
        assert isinstance(conf, Tag)

        name = name.find("td", {"class": "ui_group_alias"})
        assert isinstance(name, Tag)
        name = name.get_text(strip=True)

        conf = conf.find("table", {"class": "groupMaps"})
        assert isinstance(conf, Tag)

        maps = conf.find_all("table", {"class": "groupMaps"})
        # TODO: parse

    return result
