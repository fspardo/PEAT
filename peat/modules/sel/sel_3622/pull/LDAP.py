"""
Get data from /LDAP.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622


def pull_ldap_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field | Description |
    |-------|-------------|
    """
    result = {}

    response = session.get_endpoint("ldap_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    

    return {"ldap": result}
