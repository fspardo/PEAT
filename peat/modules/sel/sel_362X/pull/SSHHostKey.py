"""
Get data from /SSH_Host_Key.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.SSHHostKey import parse_host_keys


def pull_host_keys(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SSH_Host_Key.sel

    | Field                  | Description                     |
    |------------------------|---------------------------------|
    | `host_keys`            | Root container                  |
    | `host_keys.dsa_pubkey` | The DSA public key for the host |
    | `host_keys.rsa_pubkey` | The RSA public key for the host |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ssh_host_key")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_host_keys(soup)

    return {"host_keys": result}
