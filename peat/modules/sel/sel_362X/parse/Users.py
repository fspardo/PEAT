"""
Parse the device's users from /Users.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from .helper import *

from peat import DeviceData


def get_field(form: Tag, id: str) -> str | bool:
    """
    Get a field from a form
    """
    tag = find_tag_f(form, "input", {"id": id, "name": id})

    result = get_value(tag)

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

    form = find_table(soup, {"class": "formLayout"})

    for field in USER_FORM_FIELDS:
        id = USER_FORM_FIELDS[field]
        data = get_field(form, id)

        if field == "username" and data == "":
            raise Exception(f"Bad field entry: username is empty")

        result[field] = "N/A" if data == "" else data

    table = find_table(soup, {"id": "localUser"})

    row = find_tag_f(table, "tr", {"id": result["username"]})

    for field in USER_TABLE_FIELDS:
        result[field] = (
            get_text_of(row, "div", {"class": USER_TABLE_FIELDS[field]}) or "N/A"
        )

    return {result["username"]: result}


def parse_users(dev: DeviceData, path: Path) -> dict[str, Any]:
    """
    Parse user data
    """
    raise NotImplementedError()
