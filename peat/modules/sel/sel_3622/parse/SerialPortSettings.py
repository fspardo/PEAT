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
    "profile": "ui_ProfileName",
    "baud_rate": "ui_BaudRate",
    "data_bits": "ui_DataBit",
    "parity": "ui_Parity",
    "stop_bits": "ui_StopBit",
    "hw_flow_control": "ui_FlowControl",
    "interface": "ui_Interface",
    "alias": "ui_SerialPortAlias",
}


def parse_settings(soup: BeautifulSoup) -> list[dict[str, Any]]:
    result = []

    table = soup.find("table", {"id": "serialPorts"})
    assert isinstance(table, Tag)
    entries = table.find_all("tr", {"class": ["even", "odd"]})

    for e in entries:
        entry = {}
        assert isinstance(e, Tag)
        state = e.find("td", {"class": ["enabledSerialPort", "disabledSerialPort"]})
        if isinstance(state, Tag):  # TODO: ensure that this is sufficient
            entry["state"] = (
                "Enabled" if state.get("class") == "enabledSerialPort" else "Disabled"
            )
        else:
            entry["state"] = "Unknown"

        for c in COLUMNS:
            d = e.find("td", {"class": COLUMNS[c]})
            assert isinstance(d, Tag)
            entry[c] = d.get_text(strip=True)

        result.append(entry)

    return result
