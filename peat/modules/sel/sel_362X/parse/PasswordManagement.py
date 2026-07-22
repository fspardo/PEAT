"""
Parse data from /PasswordManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

SPANS = {
    "next_generation_date": "display_nextGenerateDate",
    "next_generation_time": "display_nextGenerateTime",
    "next_change_date": "display_nextChangeDate",
    "next_change_time": "display_nextChangeTime",
}


def parse_passwd_mgmt(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    messages = soup.find("div", {"id": "Messages"})
    assert isinstance(messages, Tag)
    messages = messages.get_text("\n", True).splitlines()
    if len(messages) > 0:
        result["messages"] = messages

    for s in SPANS:
        x = soup.find("span", {"id": SPANS[s]})
        assert isinstance(x, Tag)
        result[s] = x.get_text("", True)

    return result
