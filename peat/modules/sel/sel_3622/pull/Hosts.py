"""
Extract data from the /Hosts.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Hosts import parse_settings


def pull_hosts(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /Hosts.sel

    | Field              | Description                    |
    |--------------------|--------------------------------|
    | `hosts`            | Root container                 |
    | `hosts.[hostname]` | Mapping of hostname to address |

    """

    response = session.get_endpoint("hosts")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"hosts": parse_settings(session.gen_soup(response.text))}
