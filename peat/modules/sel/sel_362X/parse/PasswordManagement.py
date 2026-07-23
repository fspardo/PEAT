"""
Parse data from /PasswordManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData

SPANS = {
    "next_generation_date": "display_nextGenerateDate",
    "next_generation_time": "display_nextGenerateTime",
    "next_change_date": "display_nextChangeDate",
    "next_change_time": "display_nextChangeTime",
}


def parse_passwd_mgmt(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result: dict[str, str | list[str]] = {
        s: get_text_of(soup, "span", {"id": SPANS[s]}) for s in SPANS
    }

    messages = get_text_of(soup, "div", {"id": "Messages"}).splitlines()
    if len(messages) > 0:
        result["messages"] = messages

    return result
