"""
Parse data from /SerialPortSettings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

COLUMNS = {
    "profile": ["ui_ProfileName"],
    "baud_rate": ["ui_BaudRate"],
    "data_bits": ["ui_DataBit"],
    "parity": ["ui_Parity"],
    "stop_bits": ["ui_StopBit"],
    "hw_flow_control": ["ui_FlowControl"],
    "interface": ["ui_Interface"],
    "alias": ["ui_SerialPortAlias"],
}


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}

    table = soup.find("table", {"id": "serialPorts"})
    assert isinstance(table, Tag)
    entries = table.find_all("tr", {"class": ["even", "odd"]})

    for e in entries:
        entry = {}
        assert isinstance(e, Tag)
        state = e.find("td", {"class": "disabledSerialPort"})
        if isinstance(state, Tag):
            entry["state"] = "Disabled"
        else:
            entry["state"] = "Enabled"

        for c in COLUMNS:
            d = e.find("td", {"class": COLUMNS[c]})
            assert isinstance(d, Tag)
            entry[c] = d.get_text(strip=True)

        logger.debug(
            f"/// {entry['alias']} is {entry['state']} (baud={entry['baud_rate']}, db={entry['data_bits']}, p={entry['parity']}, sb={entry['stop_bits']}, hwfc={entry['hw_flow_control']}, if={entry['interface']})"
        )

        alias = entry["alias"]
        del entry["alias"]
        result[alias] = entry

    return result
