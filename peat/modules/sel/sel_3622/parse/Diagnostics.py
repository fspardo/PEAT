"""
Parse data from /Diagnostics.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_diagnostics(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse the page
    """
    result = {}

    pre = soup.find("pre", {"id": "diagnosticsText"})
    assert isinstance(pre, Tag)
    pre = pre.get_text("\n", True).splitlines()

    result["content"] = pre

    return result
