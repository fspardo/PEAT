"""
Get data from /WebServer.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.WebServer import parse_addresses, parse_global_config


def pull_web_server_config(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /WebServer.sel or /ManagementInterface.sel

    | Field                                         | Description                                                         |
    |-----------------------------------------------|---------------------------------------------------------------------|
    | `web_server`                                  | Root container                                                      |
    | `web_server.port`                             | Port number for web server                                          |
    | `web_server.session_timeout`                  | How long, in minutes, before a session is timed out                 |
    | `web_server.certificate`                      | The certificate used to create and maintain SSL connections         |
    | `web_server.listeners`                        | List of listeners for the web server                                |
    | `web_server.listeners.[alias].ip`             | IP Address                                                          |
    | `web_server.listeners.[alias].vlan_id`        | VLAN ID                                                             |
    """

    logger.debug("Pulling page...")
    response = None
    if dev._cache["VERSION"] > 200:
        response = session.get_endpoint("management_interface")
    else:
        response = session.get_endpoint("web_server")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_global_config(soup)
    result["listeners"] = parse_addresses(soup)

    return {"web_server": result}
