"""
Get data from /PasswordManagement.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.PasswordManagement import parse_passwd_mgmt


def pull_passwd_mgmt(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /PasswordManagement.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("password_management")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_passwd_mgmt(soup)

    return {"password_mgmt": result}
