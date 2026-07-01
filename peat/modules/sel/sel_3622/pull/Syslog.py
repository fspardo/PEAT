"""
Get data from /Syslog.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Syslog import parse_settings


def pull_syslog_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /Syslog.sel

    | Field | Description |
    |-------|-------------|
    |       |             |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("syslog")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    logger.debug("Parsing page...")
    return parse_settings(session.gen_soup(response.text))
