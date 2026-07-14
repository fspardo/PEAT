"""
Parse the device's users from /Users.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData
from peat.consts import BS4_PARSER

from pathlib import Path


def get_field(form: Tag, id: str) -> str | bool:
    """
    Get a field from a form
    """
    tag = form.find("input", {"id": id, "name": id})
    if not isinstance(tag, Tag):
        raise Exception(f"Could not find form field {id}")

    result = tag.get("value")
    if not isinstance(result, str):
        raise Exception("Bad type")

    if tag.get("type") == "checkbox":
        result = result == "true"

    return result


USER_FORM_FIELDS = {
    "username": "Username",
    "first_name": "FirstName",
    "last_name": "LastName",
    "title": "Title",
    "division": "Division",
    "identification": "EmployeeIdentification",
    "address": "Address",
    "city": "City",
    "state": "State",
    "country": "Country",
    "postal_code": "PostalCode",
    "work_phone": "WorkPhone",
    "mobile_phone": "MobilePhone",
    "email": "Email",
    "admin": "Admin",
    "enabled": "Enabled",
}

USER_TABLE_FIELDS = {
    "created": "ui_CreationDate",
    "last_login": "ui_LastLoginDate",
    "last_password_update": "ui_PasswordModDate",
}


def parse_user_info(dev: DeviceData, soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse an individual user's data (must be a /Users_Form.sel page)
    """
    result = {}

    form = soup.find("table", {"class": "formLayout"})
    if not isinstance(form, Tag):
        raise Exception("Failed to find update form")

    for field in USER_FORM_FIELDS:
        id = USER_FORM_FIELDS[field]
        data = get_field(form, id)

        if field == "username" and data == "":
            raise Exception(f"Bad field entry: username is empty")

        result[field] = "N/A" if data == "" else data

    table = soup.find("table", {"id": "localUser"})
    if not isinstance(table, Tag):
        raise Exception("Failed to find user list")

    row = table.find("tr", {"id": result["username"]})
    if not isinstance(row, Tag):
        raise Exception(f"Failed to find row corresponding to {result['username']}")

    for field in USER_TABLE_FIELDS:
        id = USER_TABLE_FIELDS[field]
        time = row.find("div", {"class": id})
        result[field] = (
            "N/A" if not isinstance(time, Tag) else time.get_text(strip=True)
        )

    return {result["username"]: result}


def parse_users(dev: DeviceData, path: Path) -> dict[str, Any]:
    """
    Parse user data
    """
    raise NotImplementedError()
