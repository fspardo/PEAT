"""
Parse data from /RADIUS.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Final

from loguru import logger

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData

from pathlib import Path

SETTINGS_TABLE_CHECKBOXES: Final[dict[str, str]] = {
    "enabled": "radius_auth",
    "accounting_enabled": "radius_acct",
    "use_encrypted_usernames": "encrypted_username",
    "log_accounting_updates": "syslog",
    "verify_server_identity": "verify_cert",
}

SETTINGS_TABLE_HOST_DROPDOWNS: Final[dict[str, str]] = {
    "primary_server": "Phost",
    "secondary_server": "Shost",
}

SETTINGS_TABLE_HOST_IP_ADDR: Final[dict[str, list[str]]] = {
    "primary_server": [
        "IPAddress_1P",
        "IPAddress_2P",
        "IPAddress_3P",
        "IPAddress_4P",
    ],
    "secondary_server": [
        "IPAddress_1S",
        "IPAddress_2S",
        "IPAddress_3S",
        "IPAddress_4S",
    ],
}

SETTINGS_TABLE_HOST_PORTS: Final[dict[str, dict[str, tuple[str, int]]]] = {
    "primary_server": {
        "auth": ("p_auth_port", 1812),
        "acct": ("p_acct_port", 1813),
    },
    "secondary_server": {
        "auth": ("s_auth_port", 1812),
        "acct": ("s_acct_port", 1813),
    },
}


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}
    get_host_ports = []

    table = soup.find("table", {"id": "RADIUSSettingsTable"})
    if not isinstance(table, Tag):
        raise Exception("Could not find config table")

    for checkbox in SETTINGS_TABLE_CHECKBOXES:
        v = table.find("input", {"name": SETTINGS_TABLE_CHECKBOXES[checkbox]})
        assert isinstance(v, Tag)
        result[checkbox] = v.get("checked", "no") == "checked"

    for dropdown in SETTINGS_TABLE_HOST_DROPDOWNS:
        # Get the dropdown item in the table
        v = table.find("select", {"id": SETTINGS_TABLE_HOST_DROPDOWNS[dropdown]})
        assert isinstance(v, Tag)
        # Get the selected option
        s = v.find("option", {"selected": "selected"})
        assert isinstance(s, Tag)
        # Get the IP address if the selected item is "IP Address"
        if s.get("value", "0") == "0":
            # Assert that the dropdown is recognized
            if dropdown in SETTINGS_TABLE_HOST_IP_ADDR:
                # Get the IP address
                addr_parts = []
                for part in SETTINGS_TABLE_HOST_IP_ADDR[dropdown]:
                    v = table.find("input", {"id": part})
                    assert isinstance(v, Tag)
                    value = v.get("value")
                    if value == "":
                        addr_parts = []
                        break
                    else:
                        addr_parts.append(value)
                # If incomplete, not configured
                if len(addr_parts) != 4:
                    result[dropdown] = "N/A"
                else:
                    result[dropdown] = {"address": ".".join(addr_parts)}
                    get_host_ports.append(dropdown)
        else:
            # Get the name of the host being used
            result[dropdown] = {"hostname": s.get_text(strip=True)}
            get_host_ports.append(dropdown)

    # For hosts that have an address, get their ports as well.
    for host in get_host_ports:
        if host in SETTINGS_TABLE_HOST_PORTS:
            for portname in SETTINGS_TABLE_HOST_PORTS[host]:
                p, d = SETTINGS_TABLE_HOST_PORTS[host][portname]
                v = table.find("input", {"id": p})
                assert isinstance(v, Tag)
                port = v.get("value", "")
                assert isinstance(port, str)

                if port == "":
                    port = d
                result[host][portname] = int(port)

    v = table.find("select", {"name": "RADIUSAuthTypeId"})
    assert isinstance(v, Tag)
    s = v.find("option", {"selected": "selected"})
    assert isinstance(s, Tag)
    result["auth_type"] = s.get_text(strip=True)

    v = table.find("input", {"id": "message_timeout"})
    assert isinstance(v, Tag)
    result["timeout"] = v.get("value")

    return {"radius": result}
