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


def parse_logs(csv: list[str]) -> list[dict[str, Any]]:
    result = []

    headers = [s.lower() for s in csv[0].split(",")]

    i = 1
    while i < len(csv):
        line = csv[i]
        while line[-1] != "'":  # Syslog messages are quoted
            i += 1
            line += " " + csv[i].strip()

        line.split(",")

        result.append(
            {
                headers[0]: int(line[0]),
                headers[1]: line[1] != "f",
                headers[2]: line[2],
                headers[3]: line[3],
                headers[4]: line[4],
                headers[5]: line[5],
                headers[6]: ",".join(line[6:]),
            }
        )

        i += 1

    result.sort(key=lambda x: x["id"])

    return result
