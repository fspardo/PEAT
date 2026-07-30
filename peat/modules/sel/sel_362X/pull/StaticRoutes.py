"""
Get data from /StaticRoutes.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP362X
from ..parse.StaticRoutes import parse_static_routes


def pull_static_routes(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pulls data from the /StaticRoutes.sel endpoint
    """

    response = session.get_endpoint("static_routes")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Status code {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    return {"static_routes": parse_static_routes(soup)}
