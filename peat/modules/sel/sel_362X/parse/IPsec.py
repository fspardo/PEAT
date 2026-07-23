"""
Parse data from /IPsec.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_connections(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    enabled = find_tag_f(soup, "input", {"id": "Enabled"})
    enabled = enabled.get("checked") == "checked"

    drop_on_ocsp_loss = find_tag_f(soup, "input", {"id": "DropOCSP"})
    drop_on_ocsp_loss = drop_on_ocsp_loss.get("checked") == "checked"

    result["enabled"] = enabled
    result["ocsp_loss"] = "Drop" if drop_on_ocsp_loss else "Keep"

    table = find_table(soup, {"id": "IPsecList"})
    rows = get_table_rows(table)

    connections = []

    for row in rows:
        r = {}
        # Each group of lines handles different fields. Each will get and parse each respective field as necessary.
        local_nets = [
            {"name": x[0], "subnet": x[1]}
            for x in [
                x.get_text(";", True).split(";")
                for x in find_tags(row, "td", {"class": "localNetwork"})
            ]
        ]

        local_gw = get_text_of(row, "td", {"class": "LGAlias"})
        local_gwip = get_text_of(row, "td", {"class": "LGIP"})
        cxfwd = get_text_of(row, "td", {"class": "connectionForward"})

        remote_nets = [
            {"name": x[0], "subnet": x[1]}
            for x in [
                x.get_text(";", True).split(";")
                for x in find_tags(row, "td", {"class": "remoteNetwork"})
            ]
        ]

        remote_gw = get_text_of(row, "td", {"class": "RGAlias"})
        remote_gwip = get_text_of(row, "td", {"class": "remoteGateway"})

        r["local"] = {
            "networks": local_nets,
            "gateway": {"alias": local_gw, "address": local_gwip},
        }

        r["auth"] = cxfwd

        r["remote"] = {
            "networks": remote_nets,
            "gateway": {"alias": remote_gw, "address": remote_gwip},
        }

        connections.append(r)

    result["connections"] = connections

    return result
