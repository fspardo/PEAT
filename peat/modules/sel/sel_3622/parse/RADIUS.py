"""
Parse data from /RADIUS.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from loguru import logger

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData
from peat.consts import BS4_PARSER

from pathlib import Path


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}

    return {"users": {"radius": result}}
