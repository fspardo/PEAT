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
from ..parse.LDAP import parse_settings
from loguru import logger


def pull_ldap_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field                                    | Description                                             |
    |------------------------------------------|---------------------------------------------------------|
    | `users.ldap`                             | Container for parsed data                               |
    | `users.ldap.config`                      | Global configuration                                    |
    | `users.ldap.config.enabled`              | Whether LDAP is enabled                                 |
    | `users.ldap.config.user_id_attribute`    | Attribute to use for the user's username                |
    | `users.ldap.config.sync_interval`        | How often (in hours) to sync with the LDAP server       |
    | `users.ldap.config.search_base`          | <UNKNOWN>                                               |
    | `users.ldap.config.bind_dn`              | <UNKNOWN>                                               |
    | `users.ldap.servers`                     | A list of servers to search                             |
    | `users.ldap.servers.[hostname]`          | The hostname of the server entry                        |
    | `users.ldap.servers.[hostname].priority` | The priority of this server                             |
    | `users.ldap.servers.[hostname].port`     | The port number to connect to                           |
    | `users.ldap.attributes`                  | The list of attributes to read from the LDAP server     |
    | `users.ldap.attributes.[label]`          | The attribute label, mapped to its LDAP attribute       |
    | `users.ldap.group_mappings`              | A list of group mappings.                               |
    | `users.ldap.group_mappings.[role]`       | The name of the role (tech/admin), with its list of DNs |
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("ldap_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)
    logger.debug("Parsing page...")
    result = parse_settings(soup)

    return result
