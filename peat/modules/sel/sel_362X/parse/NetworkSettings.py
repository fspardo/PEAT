"""
Extract data from the /NetworkSettings.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData


def get_global_cfg(
    soup: BeautifulSoup,
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

    return result


def get_nics(
    soup: BeautifulSoup,
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
        # Ignore images without an alt text
        if not "alt" in img.attrs:
            continue

        # Get information from the alt text, as it says practically everything
        assert isinstance(img, Tag)  # Sanity check
        alt = img.attrs["alt"]
        assert isinstance(alt, str)  # Sanity check
        data = alt.split(" - ")

        result[data[0]] = {"status": data[1], "configured": data[2]}

    return result


def get_addresses(
    soup: BeautifulSoup,
) -> tuple[
    dict[Literal["interface", "ip", "vlan", "webserver"], Any],
    dict[str, list[str]],
]:
    """
    Retrieve network addresses
    """
    table = soup.find("table", {"id": "EthernetAddress"})
    assert isinstance(table, Tag)  # Table should exist

    entries = table.find_all("tr")[1:]  # Skip title

    def get_row(
        row: Tag,
    ) -> tuple[
        str,
        dict[Literal["interface", "ip", "vlan", "webserver"], Any],
        bool,
    ]:
        repr = {}

        alias = row.find("td", {"class": "ui_AddressAlias"})
        if isinstance(alias, Tag):
            alias = alias.get_text(strip=True)
        else:
            alias = ""

        col = row.find("td", {"class": "ui_InterfaceAlias"})
        assert isinstance(col, Tag)
        repr["interface"] = col.get_text(strip=True)

        col = row.find("td", {"class": "ui_IP"})
        assert isinstance(col, Tag)
        repr["address"] = col.get_text(strip=True)

        col = row.find("td", {"class": "ui_VLAN"})
        assert isinstance(col, Tag)
        val = col.get_text(strip=True)  # Only include the VLAN ID if there is one
        if val.isnumeric():
            repr["vlan"] = int(val)

        col = row.find("td", {"class": "ui_WebServer"})
        assert isinstance(col, Tag)
        repr["webserver"] = col.get_text(strip=True) == "Yes"

        return alias, repr, "odd" in row.attrs["class"]

    # Parse all rows. This may be done the same regardless of the contents of the row
    parsed = [get_row(entry) for entry in entries]

    # Process the results. Bridged interfaces will all be either even or odd if they belong to the same bridge
    addresses = {}
    bridges = {}
    prev_o = True
    prev_a = ""

    for n, r, o in parsed:
        if prev_o == o:
            if not prev_a in bridges:
                bridges[prev_a] = []
            bridges[prev_a].append(r["interface"])
        else:
            prev_o = o
            prev_a = n
            addresses[n] = r

    return addresses, bridges
