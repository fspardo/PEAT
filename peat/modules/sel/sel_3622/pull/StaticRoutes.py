"""
Get data from /StaticRoutes.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from peat import DeviceData

from ..http import HTTP3622


def pull_table(session: HTTP3622) -> Tag:
    """
    Pull the table from the session
    """

    response = session.get_endpoint("static_routes")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Status code {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    table = soup.find("table", {"id": "staticRoute", "class": "fieldList"})
    if not isinstance(table, Tag):
        raise Exception("Could not get table")

    return table


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

    action = get_connection_rule(row)

    gateway = row.find("td", {"class": "remoteGateway"})
    assert isinstance(gateway, Tag)

    gateway = gateway.get_text(separator=",", strip=True).split(",")
    gateway_name = gateway[0]
    gateway_addr = gateway[1]

    remote = row.find("td", {"class": "remoteNetwork"})
    assert isinstance(remote, Tag)

    remote = remote.get_text(separator=",", strip=True).split(",")[1]

    result["action"] = action
    result["network"] = remote

    if action == "Forward":
        result["gateway_address"] = gateway_addr
        result["gateway_name"] = gateway_name

    return id, result


def extract_rows(rows: ResultSet) -> list[tuple[str, dict[str, Any]]]:
    """
    Extracts ALL rows from the result set
    """
    return [
        extract_row(row)  # Extract row data
        for row in rows
        if isinstance(row, Tag) and "id" in row.attrs
    ]


def pull_static_routes(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pulls data from the /StaticRoutes.sel endpoint

    | Field                                | Description                                                             |
    |--------------------------------------|-------------------------------------------------------------------------|
    | `static_routes`                      | Root container of the configuration                                     |
    | `static_routes.[id]`                 | Contains the configuration for a route of this name                     |
    | `static_routes.[id].action`          | The action taken by this route                                          |
    | `static_routes.[id].gateway_name`    | The name of the gateway traffic is routed to (if the action is FORWARD) |
    | `static_routes.[id].gateway_address` | The gateway traffic is routed to (if the action is FORWARD)             |
    | `static_routes.[id].network`         | The network the traffic is destined to                                  |
    """

    table = pull_table(session)
    rows = table.find_all("tr")

    return {"static_routes": {id: data for id, data in extract_rows(rows)}}
