"""
Get data from /StaticRoutes.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622
from ..parse.StaticRoutes import parse_static_routes


def pull_static_routes(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pulls data from the /StaticRoutes.sel endpoint

    | Field                                | Description                                                             |
    |--------------------------------------|-------------------------------------------------------------------------|
    | `static_routes`                      | Root container of the configuration                                     |
    | `static_routes.[id]`                 | Contains the configuration for a route of this name                     |
    | `static_routes.[id].action`          | The action taken by this route                                          |
    | `static_routes.[id].gateway_name`    | The name of the gateway traffic is routed to (if the action is FORWARD) |
    | `static_routes.[id].gateway_address` | The gateway traffic is routed to (if the action is FORWARD)             |
    | `static_routes.[id].network`         | The network the traffic is destined to                                  |
    """

    response = session.get_endpoint("static_routes")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Status code {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    return {"static_routes": parse_static_routes(soup)}
