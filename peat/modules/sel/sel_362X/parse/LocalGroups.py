"""
Parse data from /LocalGroups.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    table = soup.find("table", {"id": "local_groups"})
    if not isinstance(table, Tag):
        raise Exception("Table not found")

    rows = table.find_all("tr", attrs={"class": ["even", "odd"]}, recursive=False)

    result = {row.get("id"): [] for row in rows}

    for group in result:
        gtable = table.find("tr", {"id": f"group_{group}_users"})
        if not isinstance(gtable, Tag):
            continue

        members = gtable.find_all("td", {"class": "Alias"})

        result[group] = [member.get_text(strip=True) for member in members]

    return result
