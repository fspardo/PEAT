"""
Get data from /AllowedClients.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.AllowedClients import parse_clients


def pull_clients(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /AllowedClients.sel

    | Field                                           | Description                                                                   |
    |-------------------------------------------------|-------------------------------------------------------------------------------|
    | `ipsec`                                         | Root container                                                                |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ipsec_connections")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_clients(soup)

    return {"ipsec": result}
