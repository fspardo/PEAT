"""
Pull data from /LocalGroups.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.LocalGroups import parse_settings


def pull_local_groups(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field                  | Description                                                             |
    |------------------------|-------------------------------------------------------------------------|
    | `local_groups`         | Root container                                                          |
    | `local_groups.[group]` | Each group is an object in a dictionary, assigned an array of usernames |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("local_groups")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"local_groups": parse_settings(session.gen_soup(response.text))}
