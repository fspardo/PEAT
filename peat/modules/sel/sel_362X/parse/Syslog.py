"""
Parse data from /Syslog.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_row(tr: Tag) -> dict[str, Any]:
    ip = get_text_of_f(tr, "td", {"class": "syslog_ip"})
    port = get_text_of_f(tr, "td", {"class": "port"})
    threshold = get_text_of_f(tr, "td", {"class": "threshold"})
    description = get_text_of_f(tr, "td", {"class": "description"})

    return {
        "ip": ip,
        "port": port,
        "threshold": threshold,
        "description": description,
    }


def parse_settings(soup: BeautifulSoup) -> dict[str, Any]:
    oum = get_text_of(soup, "div", {"id": "syslog_oldest_message_numb"})

    sellvl = get_text_of(soup, "td", {"class": "loggingThresholdFG"}).removeprefix(
        "Selected Level: "
    )

    table = find_table(soup, {"id": "SyslogDestinations"})
    entries = {str(tr.get("id", "N/A")): parse_row(tr) for tr in get_table_rows(table)}

    return {
        "oldest_unacknowledged": oum,
        "threshold_level": sellvl,
        "destinations": entries,
    }
