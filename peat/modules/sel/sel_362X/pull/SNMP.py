"""
Pull data from /LocalGroups.sel.

Author: Francisco Santana
"""

from pathlib import Path
from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.SNMP import parse_mibs, parse_settings


def pull_snmp_mibs(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    logger.debug("Pulling SNMP MIBs...")

    response = session.get("SNMP_MIBs.sel")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception("Non-200 status")
    if len(response.history) > 0:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)
    t = soup.find("input", {"type": "hidden"})
    assert isinstance(t, Tag)
    t = t.get("value")
    assert t

    response = session.post(
        f"{session.url}/SNMP_MIBs.sel",
        data={"submit": "Download", "t": t},
    )

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception("Non-200 status")
    if len(response.history) > 0:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Writing MIBs ZIP file")
    dev.write_file(response.content, "MIBS.zip")

    return parse_mibs(dev, "MIBS.zip")


def pull_snmp_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("snmp_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")

    result = parse_settings(session.gen_soup(response.text))

    try:
        result.update(pull_snmp_mibs(dev, session))
    except Exception as e:
        logger.error(f"Failed to pull SNMP MIBs files: {e}")

    return {"snmp": result}
