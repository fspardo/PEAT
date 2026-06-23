"""
Parse data from /LDAP.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData
from peat.consts import BS4_PARSER

from pathlib import Path


def parse_settings(content: BeautifulSoup) -> dict[str, Any]:
    return {}


def parse_ldap(dev: DeviceData, path: Path) -> dict[str, Any]:
    """
    Parse LDAP settings
    """

    raise NotImplementedError()
