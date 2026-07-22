"""
Parse data from /SerialPortProfiles.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

COLUMNS = {
    "name": ["ui_ProfileName"],
    "baud_rate": ["ui_BaudRate"],
    "data_bits": ["ui_DataBit"],
    "parity": ["ui_Parity"],
    "stop_bits": ["ui_StopBit"],
    "hw_flow_control": ["ui_FlowControl"],
    "comm_interface": ["ui_Interface"],
    "frame_size": ["ui_FrameSize"],
}


def parse_profiles(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}

    table = soup.find("table", {"id": "serialPorts"})
    assert isinstance(table, Tag)
    entries = table.find_all("tr", {"class": ["even", "odd"]})

    for e in entries:
        entry = {}
        assert isinstance(e, Tag)

        for c in COLUMNS:
            d = e.find("td", {"class": COLUMNS[c]})
            assert isinstance(d, Tag)
            entry[c] = d.get_text(strip=True)

        name = entry["name"]
        del entry["name"]
        result[name] = entry

    return result
