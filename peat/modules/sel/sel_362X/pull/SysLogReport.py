"""
Get data from /SysLogReport.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.SysLogReport import parse_logs


def pull_syslog_report(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SysLogReport.sel

    Logs are sorted by ID, in ascending order
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("system_logs")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)
    t = soup.find("input", {"type": "hidden", "name": "t"})

    if not isinstance(t, Tag):
        raise Exception("Failed to find token")

    t = t.get("value")

    response = session.get(f"SysLogReport.sel?submit=download&t={t}")

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

    return {"syslog_report": parse_logs(csv)}
