"""
Parse data from /LDAP.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

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
    for key in GLOBAL_SETTINGS:
        config[key] = table.find("td", {"id": GLOBAL_SETTINGS[key]})
    result["config"] = config

    table = soup.find("table", {"id": LDAP_SERVER_LIST_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    list = table.find_all("tr")[1:]

    servers = {}
    for row in list:
        r = {}
        for key in LDAP_SERVER_LIST:
            r[key] = row.find("td", {"id": key})
        hostname = r["ldap_hostname"]
        del r["ldap_hostname"]
        servers[hostname] = r
    result["servers"] = servers

    table = soup.find("table", {"id": ATTRIBUTE_STRINGS_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    attrs = {}
    for pair in ATTRIBUTE_STRINGS:
        p = {}
        for k in pair:
            p[k] = table.find("td", {"id": pair[k]})
        attrs[p["label"]] = p["attribute"]
    result["attributes"] = attrs

    table = soup.find("table", {"id": GROUP_MAPPINGS_NAME})
    if not isinstance(table, Tag):
        raise Exception("Could not find server list table")

    list = table.find_all("tr")[1:]

    groupmaps = {}
    for row in list:
        r = {}
        for key in GROUP_MAPPINGS:
            r[key] = row.find("td", {"id": GROUP_MAPPINGS[key]})

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
