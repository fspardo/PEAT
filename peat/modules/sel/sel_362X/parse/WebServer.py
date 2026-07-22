"""
Parse data from /WebServer.sel.

Authors: Nehal Mohamed Ameen <nmameen@sandia.gov>
         Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def get_txt_input_value(soup: BeautifulSoup | Tag, eid: str) -> str:
    """Get the value of a text input by ID"""
    tag = soup.find("input", {"type": "text", "id": eid})
    assert isinstance(tag, Tag)

    value = tag.get("value", "")
    assert isinstance(value, str)

    return value.strip()


def get_select_input_value(soup: BeautifulSoup | Tag, eid: str) -> str | None:
    tag = soup.find("select", {"id": eid})
    assert isinstance(tag, Tag)

    opt = tag.find("option", {"selected": "selected"})
    if not opt:
        return None

    return opt.get_text("", True)


def get_checkbox_value(soup: BeautifulSoup | Tag, eid: str) -> bool:
    tag = soup.find("input", {"type": "checkbox", "id": eid})
    assert isinstance(tag, Tag)

    value = tag.get("value")
    assert isinstance(value, str)

    return value == "true"


def element_exists(soup: BeautifulSoup | Tag, tagty: str, eid: str) -> bool:
    tag = soup.find(tagty, {"id": eid})

    return isinstance(tag, Tag)


def parse_global_config(soup: BeautifulSoup) -> dict[str, Any]:
    table = soup.find("table", {"id": "WebInterface"})
    assert isinstance(table, Tag)

    sess_timeout = get_txt_input_value(table, "SessionTimeout")
    cert = get_select_input_value(table, "X509Certificate")
    if not cert:
        cert = "Default"

    result = {
        "port": int(get_txt_input_value(table, "Port")),
        "session_timeout": f"{sess_timeout} minutes",
        "cert": cert,
    }

    if element_exists(table, "input", "ServicePortEnabled"):
        result["service_port"] = {}
        result["service_port"]["enabled"] = get_checkbox_value(table, "ServicePortEnabled")
        result["service_port"]["port"] = int(get_txt_input_value(table, "ServicePortNumber"))

    return result


def parse_listeners(soup: BeautifulSoup) -> dict[str, Any]:
    COLUMNS = {
        "alias": "ui_AddressAlias",
        "ip": "ui_IP",
        "vlan_id": "ui_VLAN",
    }

    table = soup.find("table", {"id": "webServer"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["even", "odd"]})
    result = {}

    for row in rows:
        assert isinstance(row, Tag)
        r = {}

        for col in COLUMNS:
            x = row.find("td", {"class": COLUMNS[col]})
            assert isinstance(x, Tag)
            r[col] = x.get_text("", True)

        a = r["alias"]
        del r["alias"]
        result[a] = r

    return result
