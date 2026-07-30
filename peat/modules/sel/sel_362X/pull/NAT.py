"""
Pull data from /LocalGroups.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.NAT import parse_nat_config

def pull_nat_config(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the device's NAT config    
    """
    
    logger.debug("Pulling page...")
    response = session.get_endpoint("nat")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"NAT": parse_nat_config(session.gen_soup(response.text))}