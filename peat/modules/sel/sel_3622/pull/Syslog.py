"""
Get data from /Syslog.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Syslog import parse_settings


def pull_syslog_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /Syslog.sel

    | Field                                             | Description                                                           |
    |---------------------------------------------------|-----------------------------------------------------------------------|
    | `syslog_settings`                                 | Root container                                                        |
    | `syslog_settings.oldest_unacknowledged`           | Oldest unacknowledged syslog entry                                    |
    | `syslog_settings.threshold_level`                 | What level of error is logged on the system                           |
    | `syslog_settings.destinations`                    | Contains a dictionary of destination servers and their configurations |
    | `syslog_settings.destinations.[name]`             | The name of the destination, mapped to its configuration              |
    | `syslog_settings.destinations.[name].ip`          | The IP address of the syslog destination server                       |
    | `syslog_settings.destinations.[name].port`        | The port number to which logs are sent                                |
    | `syslog_settings.destinations.[name].threshold`   | The level at which a log must be to be sent to this destination       |
    | `syslog_settings.destinations.[name].description` | The description associated with the destination                       |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("syslog")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"syslog_settings": parse_settings(session.gen_soup(response.text))}
