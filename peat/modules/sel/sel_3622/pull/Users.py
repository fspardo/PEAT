"""
Pull the device's users from /Users.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4.element import Tag

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Users import parse_user_info


def pull_user_info(dev: DeviceData, session: HTTP3622, row: Tag) -> dict[str, Any]:
    result = {}

    # Get the URL from the Update button
    update = row.find("td", {"title": "Update"})
    if not isinstance(update, Tag):
        return {}
    # Get redirect path
    ref = update.get("href")

    # Get the username
    username = row.find("td", {"class": "ui_Username"})
    if not isinstance(username, Tag):
        return {}
    username = username.get_text(strip=True)

    # Get that page
    response = session.get(ref)
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    result.update(parse_user_info(dev, response.text))

    return result


def pull_users(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    result = {}

    # Get the page
    response = session.get_endpoint("accounts")
    # Check response
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    # Save main HTML file to root
    dev.write_file(response.text, "Users.sel.html", False, dev.get_out_dir() / "pulled")

    # Parse
    soup = session.gen_soup(response.text)

    # Extract table
    table = soup.find("table", {"id": "localUser"})
    if not isinstance(table, Tag):
        raise Exception("Could not find data table")

    # Parse rows
    rows = table.find_all("tr")[1:]
    for row in rows:
        result.update(pull_user_info(dev, session, row))

    return {"users": result}
