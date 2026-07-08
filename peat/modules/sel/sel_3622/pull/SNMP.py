"""
Pull data from /LocalGroups.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.SNMP import parse_mibs, parse_settings


def pull_snmp_mibs(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
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
        raise Exception("Redirected")

    logger.debug("Writing MIBs ZIP file")
    dev.write_file(response.content, "MIBS.zip")

    return parse_mibs(dev, "MIBS.zip")


def pull_snmp_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field                          | Description                                                                |
    |--------------------------------|----------------------------------------------------------------------------|
    | `snmp`                         | Root container                                                             |
    | `snmp.enabled`                 | Whether SNMP is enabled                                                    |
    | `snmp.engine_id`               | The engine ID reported by the device                                       |
    | `snmp.profiles`                | The set of configured profiles                                             |
    | `snmp.profiles[i].name`        | Profile name                                                               |
    | `snmp.profiles[i].version`     | SNMP versions used by the profile                                          |
    | `snmp.profiles[i].auth`        | SNMP authentication protocol                                               |
    | `snmp.profiles[i].encrypton`   | SNMP encryption protocol                                                   |
    | `snmp.profiles[i].permissions` | Permissions associated with the profile                                    |
    | `snmp.servers`                 | The set of configured trap servers                                         |
    | `snmp.servers[i].alias`        | The alias for this trap server                                             |
    | `snmp.servers[i].address`      | The IP address of this trap server                                         |
    | `snmp.servers[i].profile`      | The profile being used for this trap server                                |
    | `snmp.servers[i].traps`        | What this server is trapping from this device                              |
    | `snmp.mibs`                    | The list of Management Information Base (MIB) objects provided by this SEL |
    | `snmp.mibs.[name]`             | The name of a SNMP MIB file provided by the SEL                            |
    | `snmp.mibs.[name].sha256sum`   | The SHA256 checksum of the contents of this MIBs                           |
    | `snmp.mibs.[name].content`     | The contents of this MIB file, split by line                               |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("snmp_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    logger.debug("Parsing page...")

    result = parse_settings(session.gen_soup(response.text))

    try:
        result.update(pull_snmp_mibs(dev, session))
    except Exception as e:
        logger.error(f"Failed to pull SNMP MIBs files: {e}")

    return {"snmp": result}
