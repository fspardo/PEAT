"""
Parse data from /PortMappings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_mappings(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    table = find_table(soup, {"id": "PortMappingGroups"})

    rows = find_tags(table, "tr", {"class": ["odd", "oddProxy", "even", "evenProxy"]})
    # Convert into tuples; this makes parsing simpler.
    rows = [(rows[i * 2], rows[i * 2 + 1]) for i in range(len(rows) // 2)]

    for name, conf in rows:
        # We need all of these to be tags.
        name = get_text_of(name, "td", {"class": "ui_group_alias"})

        conf = find_table(conf, {"class": "groupMaps"})
        maps = find_tags(conf, "table", {"class": "groupMaps"})

        parsed = []

        # TODO: figure out how the odd table at the bottom of the row is populated, then try to populate it to parse it
        # For now, we'll ignore it

        for map in maps:
            x = {}

            # Device name
            x["alias"] = get_text_of(map, "div", {"class": "groupDeviceLabelActive"})

            # Check if the image is of a serial device.
            comm_dev_serial = find_tag(
                map,
                "div",
                {"class": ["groupSerialPortInactive", "groupSerialPortActive"]},
            )
            # If it is, "Serial". Otherwise, "Ethernet".
            x["device"] = "Serial" if comm_dev_serial else "Ethernet"

            # Device listen address
            gcla = find_tag_f(map, "td", {"class": "groupCommLinkActive"})
            comm_dev_listen = find_tag(gcla, "span")
            if isinstance(comm_dev_listen, Tag):
                listen = comm_dev_listen.get_text("", True).split(":")
                if len(listen) >= 2:
                    x["listen"] = {"ip": listen[0], "port": listen[1]}
                else:
                    x["listen"] = listen

            # Protocol
            x["proto"] = get_text_of(map, "label", {"class": "commStatsProtocol"})

            # Statistics (if they exist)
            comm_stats = find_tag(map, "a", {"class": "diagnosPopUp"})
            if isinstance(comm_stats, Tag):
                lines = comm_stats.get_text(";", True).split(";")
                x["stats"] = {}

                for stat in lines:
                    s = stat.split(":")
                    # Lowercase, camelcase to match schema of JSON output
                    s[0] = s[0].lower().replace(" ", "_")

                    x["stats"][s[0]] = s[1]

            parsed.append(x)

        result[name] = parsed

    return result
