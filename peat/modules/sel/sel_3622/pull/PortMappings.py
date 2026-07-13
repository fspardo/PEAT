"""
Get data from /PortMappings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.PortMappings import parse_mappings


def pull_port_mappings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /PortMappings.sel

    | Field                                         | Description                                                         |
    |-----------------------------------------------|---------------------------------------------------------------------|
    | `port_mappings`                               | Root container                                                      |
    | `port_mappings.[name]`                        | Contains configuration data for a mapping of that name              |
    | `port_mappings.[name].alias`                  | The name of the interface or listener used for this connection      |
    | `port_mappings.[name].device`                 | The type of the device (Serial or Ethernet)                         |
    | `port_mappings.[name].proto`                  | The name of the protocol used for the communication                 |
    | `port_mappings.[name].stats`                  | Statistics for the port, if available                               |
    | `port_mappings.[name].listen`                 | The listening address of the port, if available                     |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("port_mappings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Inspecting contents...")

    result = parse_mappings(soup)

    return {"port_mappings": result}
