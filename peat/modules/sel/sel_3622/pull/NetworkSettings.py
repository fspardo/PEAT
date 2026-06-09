"""
Extract data from the /NetworkSettings.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622


def get_global_cfg(
    soup: BeautifulSoup,
) -> dict[Literal["hostname", "domain", "gateway"], Any]:
    return {}


def get_nics(
    soup: BeautifulSoup,
) -> dict[str, dict[Literal["enabled", "configured"], bool]]:
    return {}


def get_addresses(
    soup: BeautifulSoup, session: HTTP3622
) -> dict[
    str, dict[Literal["interface", "ip", "vlan", "webserver", "dhcp_client"], Any]
]:
    return {}


def pull_network_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /NetworkSettings.sel
    """

    response = session.get_endpoint("network_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)
    return {
        "network": {
            "global": get_global_cfg(soup),
            "nics": get_nics(soup),
            "addresses": get_addresses(soup, session),
        }
    }
