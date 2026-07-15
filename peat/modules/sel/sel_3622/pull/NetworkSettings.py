"""
Extract data from the /NetworkSettings.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.NetworkSettings import get_addresses, get_global_cfg, get_nics


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
