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
    soup: BeautifulSoup, session: HTTP3622
) -> dict[Literal["hostname", "domain", "gateway", "dhcp_gateway"], Any]:
    """
    Retrieve the global configuration
    """
    hostname = soup.find("td", {"id": "display_Hostname"})
    domain = soup.find("td", {"id": "display_DomainName"})
    gateway = soup.find("td", {"id": "display_Gateway"})

    assert isinstance(hostname, Tag)
    hostname = hostname.get_text("", True)
    assert isinstance(domain, Tag)
    domain = domain.get_text("", True)
    assert isinstance(gateway, Tag)
    gateway = gateway.get_text("", True)

    result = {}
    if len(hostname) > 0:
        result["hostname"] = hostname
    if len(domain) > 0:
        result["domain"] = domain
    if len(gateway) > 0:
        result["gateway"] = gateway

    # TODO: see if it is possible to somehow determine what DHCP gateway to use other than the manual default gateway

    return result


def get_nics(
    soup: BeautifulSoup, _: HTTP3622
) -> dict[str, dict[Literal["status", "configured"], bool]]:
    """
    Retrieve NIC status
    """
    table = soup.find("table", {"id": "NetworkInterfaces"})
    if not isinstance(table, Tag):
        raise Exception("Could not get Ethernet configuration table")

    entries = table.find_all("img")

    result = {}

    for img in entries:
        # Get information from the alt text, as it says practically everything
        assert isinstance(img, Tag)  # Sanity check
        alt = img.attrs["alt"]
        assert isinstance(alt, str)  # Sanity check
        data = alt.split(" - ")

        result[data[0]] = {"status": data[1], "configured": data[2]}

    return result


def get_addresses(soup: BeautifulSoup, session: HTTP3622) -> dict[
    str,
    dict[
        Literal["interface", "ip", "vlan", "webserver", "dhcp_client"],
        Any,
    ]
    | str,
]:

    return {"implemented": "not"}


def pull_network_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /NetworkSettings.sel

    | Field                                | Description                                                             |
    |--------------------------------------|-------------------------------------------------------------------------|
    | `network`                            | Root container of the configuration                                     |

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
            "global": get_global_cfg(soup, session),
            "nics": get_nics(soup, session),
            "addresses": get_addresses(soup, session),
        }
    }
