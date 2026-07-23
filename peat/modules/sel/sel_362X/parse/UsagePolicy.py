"""
Parse the device's usage policy from /UsagePolicy.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from .helper import *

from peat import DeviceData

from ..http import HTTP362X


def parse_usage_policy(soup: BeautifulSoup) -> str:
    return get_text_of_f(soup, "textarea", {"id": "UseBanner"})
