"""
Extract data from the /NetworkSettings.sel endpoint

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.NetworkSettings import get_addresses, get_global_cfg, get_nics


def pull_network_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /NetworkSettings.sel
    """

    response = session.get_endpoint("network_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    addresses, bridges = get_addresses(soup)

    return {
        "network": {
            "global": get_global_cfg(soup),
            "interfaces": get_nics(soup),
            "addresses": addresses,
            "bridges": bridges,
        }
    }
