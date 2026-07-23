"""
Parse the device's usage policy from /UsagePolicy.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData

from ..http import HTTP362X


def parse_usage_policy(soup: BeautifulSoup) -> str:
    textarea = soup.find("textarea", {"id": "UseBanner"})
    if not isinstance(textarea, Tag):
        raise Exception("Could not find text area")

    return textarea.get_text("\n", True)
