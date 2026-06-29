"""
Get data from /RADIUS.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622
from ..parse.RADIUS import parse_settings
from loguru import logger


def pull_radius_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    logger.debug("Pulling page...")
    response = session.get_endpoint("radius_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    logger.debug("Parsing page...")
    return parse_settings(session.gen_soup(response.text))
