"""
Parse data from /LocalGroups.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from hashlib import sha256
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_mibs(dev: DeviceData, path: str | Path) -> dict[str, Any]:
    """Parse the MIBS files (for now, copies the files)"""
    mibs_dir = dev.get_out_dir() / "MIBS"
    zfile = ZipFile(dev.get_out_dir() / path)
    zfile.extractall(mibs_dir)

    dev.related.files.add(path)

    result = {}
    for file in mibs_dir.iterdir():
        dev.related.files.add(file.parent / file.name)
        text = file.read_text()
        hash = sha256(text.encode()).hexdigest()

        result[str(file.name)] = {
            "sha256sum": hash,
            "content": file.read_text(),
        }

    return {"mibs": result}


PROFILES_COLUMNS = {
    "name": ["Alias"],
    "version": ["Version"],
    "auth": ["AuthenticationProtocol"],
    "encryption": ["EncryptionProtocol"],
    "permissions": ["Permissions"],
}

TRAP_SERVERS_COLUMNS = {
    "alias": ["ServerAlias"],
    "address": ["IPAddress"],
    "profile": ["ProfileAlias"],
    "traps": ["Traps"],
}


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    """Parse SNMP settings"""
    result = {}

    enabled = find_tag_f(soup, "input", {"id": "Enabled", "type": "checkbox"})
    result["enabled"] = get_value(enabled) == "true"

    eid = find_table(soup, {"id": "snmp_engine"})
    result["engine_id"] = get_text_of(eid, "td", {"class": "Alias"}).split(": ")[1]

    table = find_table(soup, {"id": "snmp_profiles"})
    profiles = get_table_rows(table)

    parsed_profiles = []
    for profile in profiles:
        p = {}
        for col in PROFILES_COLUMNS:
            r = get_text_of(profile, "td", {"class": PROFILES_COLUMNS[col]})

            if col == "permissions":
                r = [s.strip() for s in r.split(",")]

            p[col] = r
        parsed_profiles.append(p)

    result["profiles"] = parsed_profiles

    table = find_table(soup, {"id": "snmp_trap_servers"})
    trap_servers = get_table_rows(table)

    parsed_servers = []
    for server in trap_servers:
        assert isinstance(server, Tag)
        p = {}
        for col in TRAP_SERVERS_COLUMNS:
            r = get_text_of(server, "td", {"class": TRAP_SERVERS_COLUMNS[col]}, ",")

            if col == "traps":
                r = [s.strip() for s in r.split(",")]

            p[col] = r
        parsed_servers.append(p)

    result["servers"] = parsed_servers

    return result
