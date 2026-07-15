"""
Parse data from /index.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_sys_stat(table: Tag, data: dict[str, Any]):
    ROWS = {
        "ipsec_connections": "ipsecConnections",
        "web_users": "webUsers",
        "uptime": "uptime",
        "hours": "hours",
        "power_cycles": "powerCycles",
        "firewall_rules": "firewallRules",
    }

    result = {}

    for row in ROWS:
        x = table.find("td", {"id": ROWS[row]})
        assert isinstance(x, Tag)

        result[row] = x.get_text("", True)

    data["system_statistics"] = result


def parse_led_indicators(table: Tag, data: dict[str, Any]):
    cells = table.find_all("td")

    result = {}

    for cell in cells:
        assert isinstance(cell, Tag)
        txt = cell.get_text("", True).lower()
        img = cell.find("img")
        assert isinstance(img, Tag)

        imgsrc = str(img.get("src"))
        if "led_red.png" in imgsrc:
            result[txt] = "red"
        elif "led_green.png" in imgsrc:
            result[txt] = "green"
        else:
            result[txt] = "unknown"

    data["led_indicators"] = result


def parse_network_stats(table: Tag, data: dict[str, Any]):
    tables = table.find_all("table")

    nics = tables[0]
    assert isinstance(nics, Tag)
    iscx = tables[1]
    assert isinstance(iscx, Tag)

    # Do not do this if network settings failed to parse
    if "network" in data:
        nic_rows = nics.find_all("tr")
        for row in nic_rows:
            assert isinstance(row, Tag)

            row_text = row.get_text(";", True).split(";")
            name = row_text[0]
            bin = int(row_text[2].split(" ")[0])
            bout = int(row_text[3].split(" ")[0])

            if name in data["network"]["interfaces"]:
                data["network"]["interfaces"][name] = {
                    "bytes_in": bin,
                    "bytes_out": bout,
                }

    if "ipsec" in data:
        data["ipsec"]["stats"] = {}
        icsx_rows = iscx.find_all("tr")

        for row in icsx_rows:
            assert isinstance(row, Tag)

            text = row.get_text("\n", True).splitlines()
            name = text[0]
            state = text[1]
            bin = int(name[2].split(" ")[0])
            bout = int(name[3].split(" ")[0])

            data["ipsec"]["stats"][name] = {
                "state": state,
                "in": bin,
                "out": bout,
            }


def parse_version_information(table: Tag, data: dict[str, Any]):
    ROWS = {
        "serial_number": "serialNo",
        "version": "version",
        "fid": "fid",
    }

    result = {}

    for row in ROWS:
        x = table.find("td", {"id": ROWS[row]})
        assert isinstance(x, Tag)
        result[row] = x.get_text("", True)

    data["version_information"] = result


# Tables, by the first caption in that table
PARSERS = {
    "System Statistics": parse_sys_stat,
    "LED Indicators": parse_led_indicators,
    "Ethernet Connections": parse_network_stats,
    "Version Information": parse_version_information,
}


def parse_index(soup: BeautifulSoup, data: dict[str, Any]):
    dashboard = soup.find("div", {"id": "dashBoard"})
    assert isinstance(dashboard, Tag)

    tables = dashboard.find_all("table", recursive=False)

    for table in tables:
        assert isinstance(table, Tag)
        caption = table.find("caption")
        assert isinstance(caption, Tag)
        caption = caption.get_text("", True)

        if caption not in PARSERS:
            continue

        logger.info(f"Parsing table {caption}")

        PARSERS[caption](table, data)
