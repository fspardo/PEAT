"""
Parse data from /LocalGroups.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData
from zipfile import ZipFile


def parse_mibs(dev: DeviceData, path: str | Path) -> dict[str, Any]:
    mibs_dir = dev.get_out_dir() / "MIBS"
    zfile = ZipFile(dev.get_out_dir() / path)
    zfile.extractall(mibs_dir)

    dev.related.files.add(path)

    result = {}
    for file in mibs_dir.iterdir():
        dev.related.files.add(file.parent / file.name)
        result[file] = file.read_text()

    return {"mibs": result}


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    result = {}

    enabled = soup.find("input", {"id": "Enabled", "type": "checkbox"})
    assert isinstance(enabled, Tag)
    result["enabled"] = enabled.get("value") == "true"

    eid = soup.find("table", {"id": "snmp_engine"})
    assert isinstance(eid, Tag)
    eid = eid.find("td", {"class": "Alias"})
    assert isinstance(eid, Tag)
    result["engine_id" : eid.get_text(strip=True).split(": ")[1]]

    # TODO: parse the rest of the page

    return result
