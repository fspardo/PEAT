"""
Parse data from /StaticRoutes.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from .helper import *

from peat import DeviceData


def get_connection_rule(row: Tag) -> Literal["Forward", "Drop", "Reject"]:
    """
    Get the rulename of the connection (Forward, Drop, or Reject)
    """
    fwd = find_tag(row, "td", {"class": "connectionForward"})
    drp = find_tag(row, "td", {"class": "connectionDrop"})
    rej = find_tag(row, "td", {"class": "connectionReject"})

    if fwd:
        return "Forward"
    elif drp:
        return "Drop"
    elif rej:
        return "Reject"
    else:
        raise Exception("Could not get rule")


def extract_row(row: Tag) -> tuple[str, dict[str, Any]]:
    """
    Extracts the static route configuration from a row of the table
    """
    result = {}
    id = get_attrib(row, "id") or ""
    log.debug(f"id={id}")

    action = get_connection_rule(row)
    log.debug(f"--> action={action}")

    gateway = get_text_of(row, "td", {"class": "remoteGateway"}, ",").split(",")
    log.debug(f"--> gateway={gateway}")

    remote = get_text_of(row, "td", {"class": "remoteNetwork"}, ",").split(",")[1]
    log.debug(f"--> remote={remote}")

    result["action"] = action
    result["network"] = remote

    if action == "Forward":
        result["gateway_name"] = gateway[0]
        result["gateway_address"] = gateway[1]

    return id, result


def extract_rows(rows: list[Tag]) -> list[tuple[str, dict[str, Any]]]:
    """
    Extracts ALL rows from the result set
    """
    return [extract_row(row) for row in rows]  # Extract row data


def parse_static_routes(soup: BeautifulSoup) -> dict[str, Any]:
    return {
        id: data
        for id, data in extract_rows(
            get_table_rows(
                find_table(soup, {"id": "staticRoute", "class": "fieldList"})
            )
        )
    }
