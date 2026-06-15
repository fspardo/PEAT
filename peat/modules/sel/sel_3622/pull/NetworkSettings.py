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


def get_global_cfg(  # Segregable
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


def get_nics(  # Segregable
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
) -> tuple[  # Segregable
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


def pull_network_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /NetworkSettings.sel

    | Field                                   | Description                                                                      |
    |-----------------------------------------|----------------------------------------------------------------------------------|
    | `network`                               | Root container of the configuration                                              |
    | `network.global`                        | Global configuration container                                                   |
    | `network.global.hostname`               | Hostname of the device                                                           |
    | `network.global.domain`                 | Domain the device exists in                                                      |
    | `network.global.gateway`                | Default gateway for the device                                                   |
    | `network.interfaces`                    | Lists the network interfaces for the device                                      |
    | `network.interfaces.[name]`             | The name of the interface being listed                                           |
    | `network.interfaces.[name].status`      | The status of the listed interface                                               |
    | `network.interfaces.[name].configured`  | Whether the interface is configured                                              |
    | `network.addresses`                     | The list of configured addresses on the device                                   |
    | `network.addresses.[alias]`             | The alias of the network address being listed                                    |
    | `network.addresses.[alias].interface`   | The interface to which the listed address is assigned                            |
    | `network.addresses.[alias].ip`          | The IP address assigned to the listed interface                                  |
    | `network.addresses.[alias].vlan`        | If the address is associated to a VLAN, the VLAN ID                              |
    | `network.addresses.[alias].webserver`   | Whether the web server is configured to listen to this address                   |
    | `network.bridges`                       | If bridges are present, contains a mapping of bridge names to bridged interfaces |
    | `network.bridges.[alias]`               | Contains a list of interface names associated with the bridge                    |
    """

    response = session.get_endpoint("network_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

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
