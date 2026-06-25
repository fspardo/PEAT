"""
Parse data from /LDAP.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from loguru import logger

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData
from peat.consts import BS4_PARSER

from pathlib import Path

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

    table = soup.find("table", {"id": GLOBAL_SETTINGS_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find config table")

    config = {}
    logger.debug("/// Parsing global settings...")
    for key in GLOBAL_SETTINGS:
        v = table.find("td", {"id": GLOBAL_SETTINGS[key]})
        assert isinstance(v, Tag)
        config[key] = v.get_text(strip=True)
    result["config"] = config

    table = soup.find("table", {"id": LDAP_SERVER_LIST_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    list = table.find_all("tr")[1:]

    servers = {}
    logger.debug("/// Parsing LDAP server list...")
    for row in list:
        r = {}
        for key in LDAP_SERVER_LIST:
            v = row.find("td", {"id": key})
            assert isinstance(v, Tag)
            r[key] = v.get_text(strip=True)
        hostname = r["ldap_hostname"]
        del r["ldap_hostname"]
        servers[hostname] = r
    result["servers"] = servers

    table = soup.find("table", {"id": ATTRIBUTE_STRINGS_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    attrs = {}
    logger.debug("/// Parsing attributes...")
    for pair in ATTRIBUTE_STRINGS:
        p = {}
        for k in pair:
            v = table.find("td", {"id": pair[k]})
            assert isinstance(v, Tag)
            p[k] = v.get_text(strip=True)
        attrs[p["label"]] = p["attribute"]
    result["attributes"] = attrs

    table = soup.find("table", {"id": GROUP_MAPPINGS_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    list = table.find_all("tr")[1:]

    groupmaps = {}
    logger.debug("/// Parsing group mappings...")
    for row in list:
        r = {}
        for key in GROUP_MAPPINGS:
            v = row.find("td", {"id": GROUP_MAPPINGS[key]})
            assert isinstance(v, Tag)
            r[key] = v.get_text(strip=True)

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
