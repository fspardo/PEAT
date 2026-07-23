"""
Extract data from the /NetworkSettings.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def get_global_cfg(
    soup: BeautifulSoup,
) -> dict[Literal["hostname", "domain", "gateway", "dhcp_gateway"], Any]:
    """
    Retrieve the global configuration
    """
    hostname = get_text_of(soup, "td", {"id": "display_Hostname"})
    domain = get_text_of(soup, "td", {"id": "display_DomainName"})
    gateway = get_text_of(soup, "td", {"id": "display_Gateway"})

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
    table = find_table(soup, {"id": "NetworkInterfaces"})
    entries = find_tags(table, "img")
    result = {}

    for img in entries:
        # Ignore images without an alt text
        if not "alt" in img.attrs:
            continue

        # Get information from the alt text, as it says practically everything
        data = get_attrib_f(img, "alt").split(" - ")

        result[data[0]] = {"status": data[1], "configured": data[2]}

    return result


def get_addresses(
    soup: BeautifulSoup,
) -> tuple[
    dict[str, Any],
    dict[str, list[str]],
]:
    """
    Retrieve network addresses and bridges

    The first element of the tuple is a dictionary of configuration data, while the other is 
    """
    table = find_table(soup, {"id": "EthernetAddress"})
    entries = get_table_rows(table)

    def get_row(
        row: Tag,
    ) -> tuple[
        str,
        dict[Literal["interface", "ip", "vlan", "webserver"], Any],
        bool,
    ]:
        repr = {}

        alias = get_text_of(row, "td", {"class": "ui_AddressAlias"})
        repr["interface"] = get_text_of(row, "td", {"class": "ui_InterfaceAlias"})
        repr["address"] = get_text_of(row, "td", {"class": "ui_IP"})

        val = get_text_of(row, "td", {"class": "ui_VLAN"})
        if val.isnumeric():  # Only include the VLAN ID if there is one
            repr["vlan"] = int(val)

        repr["webserver"] = get_text_of(row, "td", {"class": "ui_WebServer"}) == "Yes"

        return alias, repr, "odd" in row.attrs["class"]

    # Parse all rows. This may be done the same regardless of the contents of the row
    parsed = [get_row(entry) for entry in entries]

    # Process the results. Bridged interfaces will all be either even or odd if they belong to the same bridge
    addresses = {}
    bridges: dict[str, list] = {}
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
