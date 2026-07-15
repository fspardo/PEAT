"""
Extract data from the /index.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.index import parse_index


def pull_index(dev: DeviceData, session: HTTP3622, data: dict[str, Any]):
    """
    This works a bit differently. Some information is not available from the
    respective pages, while others are seemingly unique.

    This is to be run last.
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("dashboard")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    parse_index(soup, data)

    pass
