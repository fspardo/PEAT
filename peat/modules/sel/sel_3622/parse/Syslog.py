"""
Parse data from /Syslog.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_row(tr: Tag) -> dict[str, Any]:
    ip = tr.find("td", {"class": "syslog_ip"})
    port = tr.find("td", {"class": "port"})
    threshold = tr.find("td", {"class": "threshold"})
    description = tr.find("td", {"class": "description"})
    assert isinstance(ip, Tag)
    assert isinstance(port, Tag)
    assert isinstance(threshold, Tag)
    assert isinstance(description, Tag)

    return {
        "ip": ip.get_text(strip=True),
        "port": port.get_text(strip=True),
        "threshold": threshold.get_text(strip=True),
        "description": description.get_text(strip=True),
    }


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    oum = soup.find("div", {"id": "syslog_oldest_message_numb"})
    assert isinstance(oum, Tag)
    oum = oum.get_text(strip=True)

    sellvl = soup.find("td", {"class": "loggingThresholdFG"})
    assert isinstance(sellvl, Tag)
    sellvl = sellvl.get_text(strip=True).removeprefix("Selected Level: ")

    table = soup.find("table", {"id": "SyslogDestinations"})
    assert isinstance(table, Tag)
    entries = {
        str(tr.get("id", "N/A")): parse_row(tr)
        for tr in table.find_all("tr", {"class": ["odd", "even"]})
    }

    return {
        "syslog_settings": {
            "oldest_unacknowledged": oum,
            "threshold_level": sellvl,
            "destinations": entries,
        }
    }
