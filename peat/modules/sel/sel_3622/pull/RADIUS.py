"""
Get data from /RADIUS.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622
from ..parse.RADIUS import parse_settings


def pull_dictionary(
    dev: DeviceData,
    session: HTTP3622,
    soup: BeautifulSoup,
) -> bool:
    t = soup.find("input", {"name": "t"})
    if not isinstance(t, Tag):
        logger.error("Could not get token value")
        return False

    response = session.post_endpoint(
        "radius_settings",
        data={
            "t": t.get("value"),
            "download": "Download",
        },
    )

    if not response:
        logger.error("No response")
        return False

    if response.status_code != 200:
        logger.error("Could not pull file")
        return False

    if response.headers["Content-Type"] != "text/plain":
        logger.error("Incorrect content type")
        return False

    dev.write_file(response.text, "Dictionary.sel")
    dev.related.files.add("Dictionary.sel")
    return True


def pull_radius_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field                                | Description                                                     |
    |--------------------------------------|-----------------------------------------------------------------|
    | `radius`                             | Container for parsed data                                       |
    | `radius.enabled`                     | Whether RADIUS authentication is enabled                        |
    | `radius.accounting_enabled`          | Whether to account sign-in attempts on the remote server        |
    | `radius.use_encrypted_usernames`     | Whether to encrypt usernames in transit                         |
    | `radius.log_accounting_updates`      | Whether to log updates made while accounting RADIUS accounts    |
    | `radius.verify_server_identity`      | Whether to assert the identity of the server being connected to |
    | `radius.primary_server`              | The configuration to be used for the primary RADIUS server      |
    | `radius.secondary_server             | The configuration to be used for the secondary RADIUS server    |
    | `radius.[server]`                    | If not configured, will be configured with `N/A`                |
    | `radius.[server].address`            | The IP address of the server, if configured                     |
    | `radius.[server].hostname`           | The hostname of the server, if configured                       |
    | `radius.[server].auth`               | The port to use for authentication (default=1812)               |
    | `radius.[server].acct`               | The port to use for accounting (default=1813)                   |
    | `radius.[server].auth_type`          | The type of authentication to be used on either server          |
    | `radius.[server].timeout`            | How long, in seconds, before an attempt is timed out            |
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("radius_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.info("Pulling RADIUS dictionary...")
    if not pull_dictionary(dev, session, soup):
        logger.error("Failed to pull dictionary")

    logger.debug("Parsing page...")
    return parse_settings(soup)
