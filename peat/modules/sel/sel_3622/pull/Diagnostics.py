"""
Extract data from the /Diagnostics.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Diagnostics import parse_diagnostics


def pull_diagnostics(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /Diagnostics.sel

    | Field              | Description                    |
    |--------------------|--------------------------------|
    | `diagnostics`      | Root container                 |
    """

    response = session.get_endpoint("diagnostics")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    logger.debug("Parsing page...")
    return {"diagnostics": parse_diagnostics(session.gen_soup(response.text))}
