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

from .helper import *

from peat import DeviceData


def get_txt_input_value(soup: BeautifulSoup | Tag, eid: str) -> str:
    """Get the value of a text input by ID"""
    tag = find_tag_f(soup, "input", {"type": "text", "id": eid})

    return get_value(tag).strip()


def get_select_input_value(soup: BeautifulSoup | Tag, eid: str) -> str | None:
    tag = find_tag_f(soup, "select", {"id": eid})

    opt = find_tag(tag, "option", {"selected": "selected"})
    if not opt:
        return None

    return opt.get_text("", True)


def get_checkbox_value(soup: BeautifulSoup | Tag, eid: str) -> bool:
    tag = find_tag_f(soup, "input", {"type": "checkbox", "id": eid})
    value = tag.get("value")
    return value == "true"


def element_exists(soup: BeautifulSoup | Tag, tagty: str, eid: str) -> bool:
    return isinstance(find_tag(soup, tagty, {"id": eid}), Tag)


def parse_global_config(soup: BeautifulSoup) -> dict[str, Any]:
    table = find_table(soup, {"id": "WebInterface"})

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
        result["service_port"]["enabled"] = get_checkbox_value(
            table, "ServicePortEnabled"
        )
        result["service_port"]["port"] = int(
            get_txt_input_value(table, "ServicePortNumber")
        )

    return result


def parse_listeners(soup: BeautifulSoup) -> dict[str, Any]:
    COLUMNS = {
        "alias": "ui_AddressAlias",
        "ip": "ui_IP",
        "vlan_id": "ui_VLAN",
    }

    table = find_table(soup, {"id": "webServer"})

    rows = get_table_rows(table)
    result = {}

    for row in rows:
        r = {col: get_text_of(row, "td", {"class": COLUMNS[col]}) for col in COLUMNS}

        a = r["alias"]
        del r["alias"]
        result[a] = r

    return result
