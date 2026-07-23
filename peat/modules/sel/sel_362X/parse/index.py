"""
Parse data from /index.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

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

    data["system_statistics"] = {
        row: get_text_of(table, "td", {"id": ROWS[row]}) for row in ROWS
    }


def parse_led_indicators(table: Tag, data: dict[str, Any]):
    cells = find_tags(table, "td")

    result = {}

    for cell in cells:
        txt = cell.get_text("", True).lower()
        img = find_tag_f(cell, "img")

        imgsrc = str(img.get("src"))
        if "led_red.png" in imgsrc:
            result[txt] = "red"
        elif "led_green.png" in imgsrc:
            result[txt] = "green"
        else:
            result[txt] = "unknown"

    data["led_indicators"] = result


def parse_network_stats(table: Tag, data: dict[str, Any]):
    tables = find_tags(table, "table")

    nics = tables[0]
    iscx = tables[1]

    # Do not do this if network settings failed to parse
    if "network" in data:
        logger.info("Parsing Ethernet Stats")
        nic_rows = find_tags(nics, "tr")
        for row in nic_rows[1:]:
            row_text = row.get_text(";", True).split(";")
            name = row_text[0]
            bin = int(row_text[2].split(" ")[0])
            bout = int(row_text[3].split(" ")[0])

            if name in data["network"]["interfaces"]:
                data["network"]["interfaces"][name].update(
                    {
                        "bytes_in": bin,
                        "bytes_out": bout,
                    }
                )

    if "ipsec" in data:
        logger.info("Parsing IPsec Stats")
        data["ipsec"]["stats"] = {}
        icsx_rows = find_tags(iscx, "tr")

        for row in icsx_rows[1:]:
            text = row.get_text("\n", True).splitlines()
            name = text[0]
            state = text[1]
            bin = int(text[2].split(" ")[0])
            bout = int(text[3].split(" ")[0])

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

    data["version_information"] = {
        row: get_text_of(table, "td", {"id": ROWS[row]}) for row in ROWS
    }


# Tables, by the first caption in that table
PARSERS = {
    "System Statistics": parse_sys_stat,
    "LED Indicators": parse_led_indicators,
    "Ethernet Connections": parse_network_stats,
    "Version Information": parse_version_information,
}


def parse_index(soup: BeautifulSoup, data: dict[str, Any]):
    dashboard = find_tag_f(soup, "div", {"id": "dashBoard"})

    tables = find_tags(dashboard, "table", recursive=False)

    for table in tables:
        caption = get_text_of(table, "caption")

        if caption not in PARSERS:
            continue

        logger.info(f"Parsing table {caption}")

        PARSERS[caption](table, data)
