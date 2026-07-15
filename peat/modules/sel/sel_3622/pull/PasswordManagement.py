"""
Get data from /PasswordManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.PasswordManagement import parse_passwd_mgmt


def pull_passwd_mgmt(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /PasswordManagement.sel

    | Field                                | Description                                           |
    |--------------------------------------|-------------------------------------------------------|
    | `password_mgmt`                      | Root container                                        |
    | `password_mgmt.messages`             | System messages (if available)                        |
    | `password_mgmt.next_generation_date` | When the next generation is set to occur              |
    | `password_mgmt.next_generation_time` | When the next generation is set to occur              |
    | `password_mgmt.next_change_date`     | When the next change is set to occur                  |
    | `password_mgmt.next_change_time`     | When the next change is set to occur                  |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("password_management")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_passwd_mgmt(soup)

    return {"password_mgmt": result}
