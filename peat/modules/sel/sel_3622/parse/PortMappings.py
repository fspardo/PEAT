"""
Parse data from /PortMappings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_mappings(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    table = soup.find("table", {"id": "PortMappingGroups"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["odd", "oddProxy", "even", "evenProxy"]})
    # Convert into tuples; this makes parsing simpler.
    rows = [(rows[i], rows[i + 1]) for i in range(len(rows) // 2)]

    for name, conf in rows:
        # We need all of these to be tags.
        assert isinstance(name, Tag)
        assert isinstance(conf, Tag)

        name = name.find("td", {"class": "ui_group_alias"})
        assert isinstance(name, Tag)
        name = name.get_text(strip=True)

        conf = conf.find("table", {"class": "groupMaps"})
        assert isinstance(conf, Tag)

        maps = conf.find_all("table", {"class": "groupMaps"})

        parsed = []

        for map in maps:
            assert isinstance(map, Tag)

            # Link information
            comm_link = map.find("td", {"class": "groupCommLinkActive"})
            assert isinstance(comm_link, Tag)
            # Channel information
            comm_channel = map.find("td", {"class": "commChannelActive"})
            assert isinstance(comm_channel, Tag)

            x = {}

            # Device name
            comm_dev_name = comm_link.find("div", {"class": "groupDeviceLabeActive"})
            assert isinstance(comm_dev_name, Tag)
            x["alias"] = comm_dev_name.get_text("", True)

            # Check if the image is of a serial device.
            comm_dev_serial = comm_link.find(
                "div", {"class": ["groupSerialPortInactive", "groupSerialPortActive"]}
            )
            # If it is, "Serial". Otherwise, "Ethernet".
            x["device"] = "Serial" if isinstance(comm_dev_serial, Tag) else "Ethernet"

            # Device listen address
            comm_dev_listen = comm_link.find("span")
            if isinstance(comm_dev_listen, Tag):
                listen = comm_dev_listen.get_text("", True).split(":")
                if isinstance(listen, list):
                    x["listen"] = {"ip": listen[0], "port": listen[1]}
                else:
                    x["listen"] = listen

            # Protocol
            comm_proto = comm_channel.find("label", {"class": "commStatsProto"})
            assert isinstance(comm_proto, Tag)
            x["proto"] = comm_proto.get_text("", True)

            # Statistics (if they exist)
            comm_stats = comm_channel.find("a", {"class": "diagnosPopUp"})
            assert isinstance(comm_stats, Tag)
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
