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
            "content": file.read_text().splitlines(),
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

    enabled = soup.find("input", {"id": "Enabled", "type": "checkbox"})
    assert isinstance(enabled, Tag)
    result["enabled"] = enabled.get("value") == "true"

    eid = soup.find("table", {"id": "snmp_engine"})
    assert isinstance(eid, Tag)
    eid = eid.find("td", {"class": "Alias"})
    assert isinstance(eid, Tag)
    result["engine_id"] = eid.get_text(strip=True).split(": ")[1]

    table = soup.find("table", {"id": "snmp_profiles"})
    assert isinstance(table, Tag)
    profiles = table.find_all("tr", {"class": ["odd", "even"]})

    parsed_profiles = []
    for profile in profiles:
        assert isinstance(profile, Tag)
        p = {}
        for col in PROFILES_COLUMNS:
            r = profile.find("td", {"class": PROFILES_COLUMNS[col]})
            assert isinstance(r, Tag)
            r = r.get_text(strip=True)

            if col == "permissions":
                r = [s.strip() for s in r.split(",")]

            p[col] = r
        parsed_profiles.append(p)

    result["profiles"] = parsed_profiles

    table = soup.find("table", {"id": "snmp_trap_servers"})
    assert isinstance(table, Tag)
    trap_servers = table.find_all("tr", {"class": ["odd", "even"]})

    parsed_servers = []
    for server in trap_servers:
        assert isinstance(server, Tag)
        p = {}
        for col in TRAP_SERVERS_COLUMNS:
            r = server.find("td", {"class": TRAP_SERVERS_COLUMNS[col]})
            assert isinstance(r, Tag)
            r = r.get_text(separator=",", strip=True)

            if col == "traps":
                r = [s.strip() for s in r.split(",")]

            p[col] = r
        parsed_servers.append(p)

    result["servers"] = parsed_servers

    return result
