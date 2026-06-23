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
    """
    Pull extended user info
    """
    # Get the URL from the Update button
    update = row.find("a", {"title": "Update"})
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

    return parse_user_info(dev, session.gen_soup(response.text))


def pull_users(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull registered users

    | Field                                   | Description                                                             |
    |-----------------------------------------|-------------------------------------------------------------------------|
    | `local_users`                           | Root container                                                          |
    | `local_users.[username]`                | Container for an individual user's account information                  |
    | `local_users.[username].username`       | User's username                                                         |
    | `local_users.[username].first_name`     | User's forename                                                         |
    | `local_users.[username].last_name`      | User's surname                                                          |
    | `local_users.[username].title`          | User's title                                                            |
    | `local_users.[username].division`       | User's division                                                         |
    | `local_users.[username].identification` | User's identification                                                   |
    | `local_users.[username].address`        | User's address                                                          |
    | `local_users.[username].city`           | User's city                                                             |
    | `local_users.[username].state`          | User's state                                                            |
    | `local_users.[username].country`        | User's country                                                          |
    | `local_users.[username].postal_code`    | User's postal/ZIP code                                                  |
    | `local_users.[username].work_phone`     | User's work phone number                                                |
    | `local_users.[username].mobile_phone`   | User's mobile phone number                                              |
    | `local_users.[username].email`          | User's email address                                                    |
    | `local_users.[username].admin`          | Whether the user is an administrator                                    |
    | `local_users.[username].enabled`        | Whether the user's account is enabled (can log in)                      |
    """
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

    return {"local_users": result}
