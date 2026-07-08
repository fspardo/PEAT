"""
Parse data from /RADIUS.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    return {}