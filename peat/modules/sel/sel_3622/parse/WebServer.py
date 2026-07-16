"""
Parse data from /WebServer.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_global_config(soup: BeautifulSoup) -> dict[str, Any]:
    table = soup.find("table", {"id": "WebInterface"})
    assert isinstance(table, Tag)

    port = table.find("input", {"name": "Port"})
    assert isinstance(port, Tag)
    port = port.get("value")
    assert isinstance(port, str)
    port = int(port)

    sess_timeout = table.find("input", {"name": "SessionTimeout"})
    assert isinstance(sess_timeout, Tag)
    sess_timeout = sess_timeout.get("value")
    assert isinstance(sess_timeout, str)
    sess_timeout = f"{sess_timeout} minutes"

    certificates = table.find("select", {"name": "X509Certificate"})
    assert isinstance(certificates, Tag)
    cert = certificates.find("option", {"selected": "selected"})
    if not isinstance(cert, Tag):
        cert = "Default"
    else:
        cert = cert.get_text("", True)

    result = {
        "port": port,
        "session_timeout": sess_timeout,
        "cert": cert,
    }

    svc_port_enabled = table.find("input", {"name": "ServicePortEnabled"})
    if isinstance(svc_port_enabled, Tag):
        result["service_port"] = {"enabled": svc_port_enabled.get("value") == "true"}
        svc_port = table.find("input", {"name": "ServicePortNumber"})
        assert isinstance(svc_port, Tag)
        svc_port = svc_port.get("value", "0")
        assert svc_port
        result["service_port"]["port"] = svc_port

    return result


def parse_addresses(soup: BeautifulSoup) -> dict[str, Any]:
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
