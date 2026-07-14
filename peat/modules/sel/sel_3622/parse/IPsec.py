"""
Parse data from /IPsec.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_connections(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    enabled = soup.find("input", {"id": "Enabled"})
    assert isinstance(enabled, Tag)
    enabled = enabled.get("checked") == "checked"

    drop_on_ocsp_loss = soup.find("input", {"id": "DropOCSP"})
    assert isinstance(drop_on_ocsp_loss, Tag)
    drop_on_ocsp_loss = drop_on_ocsp_loss.get("checked") == "checked"

    result["enabled"] = enabled
    result["ocsp_loss"] = "Drop" if True else "Keep"

    table = soup.find("table", {"id": "IPsecList"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["odd", "even"]})

    connections = []

    for row in rows:
        r = {}
        assert isinstance(row, Tag)

        # Each group of lines handles different fields. Each will get and parse each respective field as necessary.

        local_nets = row.find_all("td", {"class": "localNetwork"})
        local_nets = [
            x.get_text(";", True).split(";") for x in local_nets if isinstance(x, Tag)
        ]
        local_nets = [{"name": x[0], "subnet": x[1]} for x in local_nets]

        local_gw = row.find("td", {"class": "LGAlias"})
        assert isinstance(local_gw, Tag)
        local_gw = local_gw.get_text("", True)

        local_gwip = row.find("td", {"class": "LGIP"})
        assert isinstance(local_gwip, Tag)
        local_gwip = local_gwip.get_text("", True)

        cxfwd = row.find("td", {"class": "connectionForward"})
        assert isinstance(cxfwd, Tag)
        cxfwd = cxfwd.get_text("", True)

        remote_nets = row.find_all("td", {"class": "remoteNetwork"})
        remote_nets = [
            x.get_text(";", True).split(";") for x in remote_nets if isinstance(x, Tag)
        ]
        remote_nets = [{"name": x[0], "subnet": x[1]} for x in remote_nets]

        remote_gw = row.find("td", {"class": "RGAlias"})
        assert isinstance(remote_gw, Tag)
        remote_gw = remote_gw.get_text("", True)

        remote_gwip = row.find("td", {"class": "remoteGateway"})
        assert isinstance(remote_gwip, Tag)
        remote_gwip = remote_gwip.get_text("", True)

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
