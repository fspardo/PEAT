"""
Get data from /SysLogReport.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.SysLogReport import parse_logs


def pull_syslog_report(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /SysLogReport.sel

    | Field                                             | Description                                                           |
    |---------------------------------------------------|-----------------------------------------------------------------------|
    | `syslog_report`                                   | Root container                                                        |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("syslog")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)
    t = soup.find("input", {"name": "t"})

    if not isinstance(t, Tag):
        raise Exception("Failed to find token")

    t = t.get("value")

    response = session.get(f"SysLogreport.sel?submit=download&t={t}")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    csv = response.text.splitlines()

    if csv[0] != "Id,Acked,Severity,Facility,Tag,Time,Message":
        raise Exception("Got incorrect data")

    logger.debug("Parsing page...")

    logs = parse_logs(csv)

    severities = {}
    facilities = {}
    tags = {}

    for log in logs:
        sev = log["severity"]
        fac = log["facility"]
        tag = log["tag"]

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
        "syslog_report": {
            "by_severity": severities,
            "by_facility": facilities,
            "by_tag": tags,
            "total_logs": len(logs),
            "logs": logs,
        }
    }
