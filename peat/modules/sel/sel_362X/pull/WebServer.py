"""
Pull the device's web server configuration from /WebServer.sel.

Authors: Nehal Mohamed Ameen
         Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.WebServer import parse_global_config, parse_listeners


def pull_web_server_config(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /WebServer.sel or /ManagementInterface.sel
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
    result["listeners"] = parse_listeners(soup)

    return {"web_server": result}
