"""
Parse data from /LDAP.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData

GLOBAL_SETTINGS_NAME = "LDAPSettingsTable"
GLOBAL_SETTINGS = {
    "enabled": "enabled",
    "user_id_attribute": "user_id_attr",
    "group_member_attribute": "group_member_attr",
    "sync_interval": "sync_interval",
    "search_base": "search_base",
    "bind_dn": "binddn",
}

LDAP_SERVER_LIST_NAME = "LDAPServersTable"
LDAP_SERVER_LIST = ["priority", "ldap_hostname", "port"]

ATTRIBUTE_STRINGS_NAME = "LDAPAttributeTable"
ATTRIBUTE_STRINGS = [
    {"label": "f_name_label", "attribute": "f_name"},
    {"label": "l_name_label", "attribute": "l_name"},
    {"label": "email_label", "attribute": "email"},
    {"label": "phone_label", "attribute": "phone"},
]

GROUP_MAPPINGS_NAME = "LDAPGroupTable"
GROUP_MAPPINGS = {
    "role": "device_role",
    "dn": "ldap_dn",
}


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}

    table = find_table(soup, {"id": GLOBAL_SETTINGS_NAME})

    logger.debug("/// Parsing global settings...")
    result["config"] = {
        key: get_text_of(table, "td", {"id": GLOBAL_SETTINGS[key]})
        for key in GLOBAL_SETTINGS
    }

    table = find_table(soup, {"id": LDAP_SERVER_LIST_NAME})

    list = get_table_rows(table)

    servers = {}
    logger.debug("/// Parsing LDAP server list...")
    for row in list:
        r = {key: get_text_of(row, "td", {"id": key}) for key in LDAP_SERVER_LIST}
        hostname = r["ldap_hostname"]
        del r["ldap_hostname"]
        servers[hostname] = r
    result["servers"] = servers

    table = find_table(soup, {"id": ATTRIBUTE_STRINGS_NAME})

    attrs = {}
    logger.debug("/// Parsing attributes...")
    for pair in ATTRIBUTE_STRINGS:
        p = {k: get_text_of(table, "td", {"id": pair[k]}) for k in pair}
        attrs[p["label"]] = p["attribute"]
    result["attributes"] = attrs

    table = find_table(soup, {"id": GROUP_MAPPINGS_NAME})

    list = get_table_rows(table)

    groupmaps = {}
    logger.debug("/// Parsing group mappings...")
    for row in list:
        r = {
            key: get_text_of(row, "td", {"id": GROUP_MAPPINGS[key]})
            for key in GROUP_MAPPINGS
        }

        if r["role"] not in groupmaps:
            groupmaps[r["role"]] = []

        groupmaps[r["role"]].push(r["dn"])
    result["group_mappings"] = groupmaps

    return result


def parse_ldap(dev: DeviceData, path: Path) -> dict[str, Any]:
    """
    Parse LDAP settings
    """

    raise NotImplementedError()
