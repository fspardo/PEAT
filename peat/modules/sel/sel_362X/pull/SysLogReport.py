"""
Get data from /SysLogReport.sel.

Author: Francisco Santana <fsantan@sandia.gov>
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

    | Field                                             | Description                                                           |
    |---------------------------------------------------|-----------------------------------------------------------------------|
    | `syslog_report`                                   | Root container                                                        |
    | `syslog_report.by_severity`                       | Count of logs by severity                                             |
    | `syslog_report.by_facility`                       | Count of logs by facility                                             |
    | `syslog_report.by_tag`                            | Count of logs by tag                                                  |
    | `syslog_report.total_logs`                        | Count of logs                                                         |
    | `syslog_report.acknowledged`                      | Count of acknowledged logs                                            |
    | `syslog_report.logs`                              | List of logs                                                          |
    | `syslog_report.logs[i].id`                        | Log ID                                                                |
    | `syslog_report.logs[i].acked`                     | Whether the log was acknowledged                                      |
    | `syslog_report.logs[i].severity`                  | The severity level of the log                                         |
    | `syslog_report.logs[i].facility`                  | The facility from which the log was generated                         |
    | `syslog_report.logs[i].tag`                       | The tag assigned to the log                                           |
    | `syslog_report.logs[i].time`                      | When this log was generated                                           |
    | `syslog_report.logs[i].message`                   | Log message                                                           |
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
