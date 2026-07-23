"""
Get data from /IPsec.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.IPsec import parse_connections


def pull_connections(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /IPsec.sel

    `$` represents an alias, to reduce the size of the table

    | Field                                           | Description                                                                   |
    |-------------------------------------------------|-------------------------------------------------------------------------------|
    | `ipsec`                                         | Root container                                                                |
    | `ipsec.enabled`                                 | Whether IPsec is enabled                                                      |
    | `ipsec.ocsp_loss`                               | "Drop" if the policy is set to drop on OCSP connection loss, "Keep" otherwise |
    | `ipsec.connections`                             | List of connections to be made or allowed through an IPsec tunnel             |
    | `ipsec.connections[i].auth`                     | Authentication method (X.509 or Passphrase)                                   |
    | `ipsec.connections[i].local`                `$` | Local network configuration                                                   |
    | `ipsec.connections[i].remote`               `$` | Remote network configuration                                                  |
    | `ipsec.connections[i].[$].networks`             | List of networks involved in the tunnel.                                      |
    | `ipsec.connections[i].[$].networks[i].name`     | The name provided to the network                                              |
    | `ipsec.connections[i].[$].networks[i].subnet`   | The subnet address of the network                                             |
    | `ipsec.connections[i].[$].gateway`              | Information about the gateway involved in the tunnel                          |
    | `ipsec.connections[i].[$].gateway.alias`        | The alias provided for the gateway, or the name of the network gateway        |
    | `ipsec.connections[i].[$].gateway.address`      | The address of the gateway                                                    |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ipsec_connections")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_connections(soup)

    return {"ipsec": result}
