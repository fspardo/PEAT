"""
Get data from /IPsec.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.IPsec import parse_connections


def pull_connections(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /IPsec.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ipsec_connections")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_connections(soup)

    return {"ipsec": result}
