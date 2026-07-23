"""
Parse data from /SerialPortSettings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

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

    table = find_table(soup, {"id": "serialPorts"})
    entries = get_table_rows(table)

    for e in entries:
        entry = {}
        state = find_tag(e, "td", {"class": "disabledSerialPort"})
        entry["state"] = "Disabled" if state else "Enabled"

        for c in COLUMNS:
            entry[c] = get_text_of(e, "td", {"class": COLUMNS[c]})

        logger.debug(
            f"/// {entry['alias']} is {entry['state']} (baud={entry['baud_rate']}, db={entry['data_bits']}, p={entry['parity']}, sb={entry['stop_bits']}, hwfc={entry['hw_flow_control']}, if={entry['interface']})"
        )

        alias = entry["alias"]
        del entry["alias"]
        result[alias] = entry

    return result
