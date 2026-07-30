"""
Get data from /RADIUS.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.RADIUS import parse_settings


def pull_dictionary(
    dev: DeviceData,
    session: HTTP362X,
    soup: BeautifulSoup,
) -> str | None:
    t = soup.find("input", {"name": "t"})
    if not isinstance(t, Tag):
        logger.error("Could not get token value")
        return None

    response = session.post_endpoint(
        "radius_settings",
        data={
            "t": t.get("value"),
            "download": "Download",
        },
    )

    if not response:
        logger.error("No response")
        return None

    if response.status_code != 200:
        logger.error("Could not pull file")
        return None

    if response.headers["Content-Type"] != "text/plain":
        logger.error("Incorrect content type")
        return None

    dev.write_file(response.text, "Dictionary.sel")
    dev.related.files.add("Dictionary.sel")
    return response.text


def pull_radius_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("radius_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_settings(soup)

    logger.info("Pulling RADIUS dictionary...")
    try:
        d = pull_dictionary(dev, session, soup)
        if not d:
            logger.error("Failed to pull dictionary")
        result["dictionary"] = d
    except Exception as e:
        logger.error(f"Error pulling dictionary: {e}")

    return {"radius": result}
