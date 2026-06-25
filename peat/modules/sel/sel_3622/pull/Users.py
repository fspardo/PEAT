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
    | `users.local`                           | Root container                                                          |
    | `users.local.[username]`                | Container for an individual user's account information                  |
    | `users.local.[username].username`       | User's username                                                         |
    | `users.local.[username].first_name`     | User's forename                                                         |
    | `users.local.[username].last_name`      | User's surname                                                          |
    | `users.local.[username].title`          | User's title                                                            |
    | `users.local.[username].division`       | User's division                                                         |
    | `users.local.[username].identification` | User's identification                                                   |
    | `users.local.[username].address`        | User's address                                                          |
    | `users.local.[username].city`           | User's city                                                             |
    | `users.local.[username].state`          | User's state                                                            |
    | `users.local.[username].country`        | User's country                                                          |
    | `users.local.[username].postal_code`    | User's postal/ZIP code                                                  |
    | `users.local.[username].work_phone`     | User's work phone number                                                |
    | `users.local.[username].mobile_phone`   | User's mobile phone number                                              |
    | `users.local.[username].email`          | User's email address                                                    |
    | `users.local.[username].admin`          | Whether the user is an administrator                                    |
    | `users.local.[username].enabled`        | Whether the user's account is enabled (can log in)                      |
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
