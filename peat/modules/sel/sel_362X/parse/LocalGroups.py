"""
Parse data from /LocalGroups.sel.

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
    table = find_table(soup, {"id": "local_groups"})

    rows = get_table_rows(find_tag_f(table, "tbody"), False)

    result = {get_attrib_f(row, "id"): [] for row in rows}

    for group in result:
        gtable = find_tag_f(table, "tr", {"id": f"group_{group}_users"})
        members = find_tags(gtable, "td", {"class": "Alias"})
        result[group] = [member.get_text(strip=True) for member in members]

    return result
