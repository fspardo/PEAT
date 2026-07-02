"""
Parse data from /Firewall.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData


def parse_rule(tag: Tag) -> dict[str, Any]:
    """Parse a row containing a rule"""
    result = {}

    try:
        strs = [
            "globalOrder",
            "ruleInterface",
            "StatusName",
            "sourcePort",
            "descProtocolRule",
            "destPort",
        ]

        def getk(tag: Tag, k: str) -> list[str]:
            v = tag.find("td", {"class": k})
            assert isinstance(v, Tag)
            return v.get_text("\n", True).splitlines()

        values = {k: getk(tag, k) for k in strs}

        result["order"] = values["globalOrder"][0].strip()
        result["interface"] = values["ruleInterface"][0].strip()
        result["name"] = values["StatusName"][0].strip()
        result["status"] = values["StatusName"][1].strip()
        result["source_address"] = values["sourcePort"][0].strip()
        result["source_port"] = values["sourcePort"][1].strip()
        # Just in case the description field ends up supporting line breaks (the text box used to fill it does)
        result["description"] = " ".join(values["descProtocolRule"][:-1]).strip()
        protorule = values["descProtocolRule"][-1].split("\u00a0")
        result["protocol"] = protorule[0].strip()
        result["action"] = protorule[-1].strip()
        result["destination_address"] = values["destPort"][0].strip()
        result["destination_port"] = values["destPort"][1].strip()
    except:
        logger.warning("Failed to parse row")

    return result


def parse_general_rules(soup: BeautifulSoup) -> dict[str, Any]:
    """Parse the general rules table"""
    keys = {
        "drop_ping": "dropPing",
        "drop_traceroute": "dropTraceroute",
        "require_encryption": "mustBeEncrypted",
        "allow_all_encrypted": "allowAllEncrypted",
    }

    def getinpt(soup: BeautifulSoup, k: str) -> str:
        v = soup.find("input", {"id": k})
        assert isinstance(v, Tag)
        v = v.get("value")
        assert isinstance(v, str)
        return v

    return {k: getinpt(soup, keys[k]) for k in keys}


def parse_rules(soup: BeautifulSoup) -> dict[str, Any]:
    """
    Parse the firewall's configuration
    """
    result = {}

    result.update(parse_general_rules(soup))

    result["rules"] = [parse_rule(row) for row in soup.find_all("tr", {"class": ["odd", "even"]})]

    return {"firewall": result}
