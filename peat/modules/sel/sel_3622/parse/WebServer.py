"""
Parse data from /WebServer.sel.

Author: Nehal Mohamed Ameen <nmameen@sandia.gov>
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger


def get_input_value(soup: BeautifulSoup, element_id: str) -> str:
    """
    Get the value of an input element by ID.
    """
    tag = soup.find("input", {"id": element_id})

    if not isinstance(tag, Tag):
        logger.warning(f"Could not find input with id={element_id}")
        return ""

    value = tag.get("value", "")

    if not isinstance(value, str):
        return str(value).strip()

    return value.strip()


def get_text_value(soup: BeautifulSoup, element_id: str) -> str:
    """
    Get text from an element by ID.
    """
    tag = soup.find(id=element_id)

    if not isinstance(tag, Tag):
        logger.warning(f"Could not find element with id={element_id}")
        return ""

    return tag.get_text(strip=True)


def parse_select_options(soup: BeautifulSoup, element_id: str) -> list[dict[str, str]]:
    """
    Parse all options from a select element.

    Returns each option's value and display text.
    """
    select = soup.find("select", {"id": element_id})

    if not isinstance(select, Tag):
        logger.warning(f"Could not find select with id={element_id}")
        return []

    options: list[dict[str, str]] = []

    for option in select.find_all("option"):
        if not isinstance(option, Tag):
            continue

        value = option.get("value", "")
        if not isinstance(value, str):
            value = str(value)

        options.append(
            {
                "id": value.strip(),
                "name": option.get_text(strip=True),
            }
        )

    return options


def parse_selected_option(soup: BeautifulSoup, element_id: str) -> str:
    """
    Parse selected option text from a select element.

    If no option is explicitly marked selected, HTML defaults to the first option.
    """
    select = soup.find("select", {"id": element_id})

    if not isinstance(select, Tag):
        logger.warning(f"Could not find select with id={element_id}")
        return ""

    selected = select.find("option", selected=True)

    if isinstance(selected, Tag):
        return selected.get_text(strip=True)

    first = select.find("option")

    if isinstance(first, Tag):
        return first.get_text(strip=True)

    return ""


def parse_web_server_addresses(soup: BeautifulSoup) -> list[dict[str, str]]:
    """
    Parse configured Web Server Addresses.

    Source table:
        <table id="webServer" class="fieldList">

    Expected columns:
    - Alias
    - IP
    - VLAN
    - Options
    """
    table = soup.find("table", {"id": "webServer"})

    if not isinstance(table, Tag):
        logger.warning("Could not find Web Server Addresses table")
        return []

    addresses: list[dict[str, str]] = []

    for row in table.find_all("tr", {"class": ["odd", "even"]}):
        if not isinstance(row, Tag):
            continue

        alias = row.find("td", {"class": "ui_AddressAlias"})
        ip = row.find("td", {"class": "ui_IP"})
        vlan = row.find("td", {"class": "ui_VLAN"})

        if not isinstance(alias, Tag) or not isinstance(ip, Tag):
            logger.warning("Skipping malformed Web Server address row")
            continue

        addresses.append(
            {
                "alias": alias.get_text(strip=True),
                "ip": ip.get_text(strip=True),
                "vlan": vlan.get_text(strip=True) if isinstance(vlan, Tag) else "",
            }
        )

    return addresses


def parse_web_server(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse the Web Server configuration page.
    """
    return {
        "server_time": get_text_value(soup, "serverTime"),
        "port": get_input_value(soup, "Port"),
        "x509_certificate": parse_selected_option(soup, "X509Certificate"),
        "x509_certificates": parse_select_options(soup, "X509Certificate"),
        "session_timeout": get_input_value(soup, "SessionTimeout"),
        "available_network_addresses": parse_select_options(soup, "NetworkAddress"),
        "addresses": parse_web_server_addresses(soup),
    }
