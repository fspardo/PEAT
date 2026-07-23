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


def parse_logs(csv: list[str]) -> dict[str, Any]:
    logs = []

    headers = [s.lower() for s in csv[0].split(",")]

    i = 1
    while i < len(csv):
        line = csv[i]
        while line[-1] != "'":  # Syslog messages are quoted
            i += 1
            line += " " + csv[i].strip()

        line = line.split(",")

        logs.append(
            {
                headers[0]: int(line[0]),
                headers[1]: line[1] != "f",
                headers[2]: line[2],
                headers[3]: line[3],
                headers[4]: line[4],
                headers[5]: line[5],
                headers[6]: ",".join(line[6:]).strip("'"),
            }
        )

        i += 1

    logs.sort(key=lambda x: x["id"])

    severities = {}
    facilities = {}
    tags = {}
    acked = 0

    for log in logs:
        sev = log["severity"]
        fac = log["facility"]
        tag = log["tag"]

        if log["acked"]:
            acked += 1

        if sev not in severities:
            severities[sev] = 1
        else:
            severities[sev] += 1
        if fac not in facilities:
            facilities[fac] = 1
        else:
            facilities[fac] += 1
        if tag not in tags:
            tags[tag] = 1
        else:
            tags[tag] += 1

    return {
        "by_severity": severities,
        "by_facility": facilities,
        "by_tag": tags,
        "total_logs": len(logs),
        "acknowledged": acked,
        "logs": logs,
    }
