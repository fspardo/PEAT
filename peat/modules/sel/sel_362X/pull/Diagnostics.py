"""
Extract data from the /Diagnostics.sel endpoint

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.Diagnostics import parse_diagnostics_R200, parse_diagnostics_R212
from ..method import AdvancedRange as AR


def pull_diagnostics(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /Diagnostics.sel
    """

    response = session.get_endpoint("diagnostics")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    soup = session.gen_soup(response.text)

    if dev._cache["VERSION"] in AR(high=200):
        return {"diagnostics": parse_diagnostics_R200(soup)}
    else:
        return {"diagnostics": parse_diagnostics_R212(soup)}
