"""
Parse data from /StaticRoutes.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger as log

from peat import DeviceData

from ..http import HTTP3622


def get_connection_rule(row: Tag) -> Literal["Forward", "Drop", "Reject"]:
    """
    Get the rulename of the connection (Forward, Drop, or Reject)
    """
    fwd = row.find("td", {"class": "connectionForward"})
    drp = row.find("td", {"class": "connectionDrop"})
    rej = row.find("td", {"class": "connectionReject"})

    if isinstance(fwd, Tag):
        return "Forward"
    elif isinstance(drp, Tag):
        return "Drop"
    elif isinstance(rej, Tag):
        return "Reject"
    else:
        raise Exception("Could not get rule")


def extract_row(row: Tag) -> tuple[str, dict[str, Any]]:
    """
    Extracts the static route configuration from a row of the table
    """
    result = {}
    id = row.attrs["id"]
    log.debug(f"id={id}")

    action = get_connection_rule(row)
    log.debug(f"--> action={action}")

    gateway = row.find("td", {"class": "remoteGateway"})
    assert isinstance(gateway, Tag)
    gateway = gateway.get_text(",").split(",")
    log.debug(f"--> gateway={gateway}")

    remote = row.find("td", {"class": "remoteNetwork"})
    assert isinstance(remote, Tag)
    remote = remote.get_text(",").split(",")[1]
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
    table = soup.find("table", {"id": "staticRoute", "class": "fieldList"})
    if not isinstance(table, Tag):
        raise Exception("Could not get table")
    rows = table.find_all("tr")

    return {id: data for id, data in extract_rows(rows[1:])}
