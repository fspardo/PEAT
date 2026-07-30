"""
Parse data from /LocalGroups.sel.

Author: Francisco Santana
"""

from pathlib import Path
from typing import Any
from re import split

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from .helper import *

from peat import DeviceData


def parse_global_config(table: Tag | BeautifulSoup) -> dict[str, Any]:
    result = {}
    CELLS = {
        "status": "display_AddressTranslationStatus",
        "network_alias": "nat_NetworkAlias",
        "subnet": "nat_IpAddress",
    }

    for cell in CELLS:
        result[cell] = get_text_of(table, attrib={"id": CELLS[cell]})

    return result


def parse_rule(row: Tag) -> dict[str, Any]:
    """Parses a row in the rules table"""
    result: dict[str, str | dict] = {}
    CELLS = {
        "alias": "ruleAlias",
        "protocol": "ruleProtocolName",
        "source": "rulePublicSource",
        "destination": "rulePrivateDestination",
        "verbose_logging": "ruleVerboseLogging",
    }

    for cell in CELLS:
        result[cell] = get_text_of(row, attrib={"class": CELLS[cell]})

    src = result["source"]
    assert isinstance(src, str)
    src = split(r"[:/]", src)
    result["source"] = {
        "address": src[0],
        "prefix": src[1],
        "port": src[2],
    }

    dst = result["destination"]
    assert isinstance(dst, str)
    dst = dst.split(":")
    result["destination"] = {
        "address": dst[0],
        "port": dst[1],
    }

    tag = find_tag(row, "span")
    if tag:
        result["message"] = get_attrib_f(tag, "title")

    return result


def parse_nat_config(soup: BeautifulSoup) -> dict[str, Any]:
    """Parses NAT config"""
    result = parse_global_config(soup)
    table = find_table(soup, {"id": "portForwardingRules"})
    rows = get_table_rows(table)

    rules = []
    for row in rows:
        rules.append(parse_rule(row))

    result["rules"] = rules

    return result
