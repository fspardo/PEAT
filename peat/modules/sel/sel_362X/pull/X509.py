"""
Get data from /X509.sel.

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.X509 import parse_certificates_advanced, parse_certificates_basic


def pull_certificates(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /X509.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("x509_certificates")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_certificates_basic(soup)

    actions = soup.find_all("tr", {"class": ["even", "odd"]})
    actions = [
        (
            r.find("td", {"class": "x509_name"}),
            r.find("a", {"title": "View"}),
            r.find("a", {"title": "Export"}),
        )
        for r in actions
        if isinstance(r, Tag)
    ]
    hrefs = {
        n.get_text("", True): (v.get("href"), e.get("href"))
        for n, v, e in actions
        if isinstance(n, Tag) and isinstance(v, Tag) and isinstance(e, Tag)
    }

    for name in hrefs:
        logger.debug(f"Pulling additional configuration data for {name}...")
        response = session.get(hrefs[name][0])

        if not response:
            raise Exception("No response")
        if response.status_code != 200:
            raise Exception(f"Got non-200 status: {response.status_code}")
        if response.history:
            raise Exception(f"Redirected to {response.history[-1].url}")

        soup2 = session.gen_soup(response.text)

        # Replace data with more advanced parse output
        result[name] = parse_certificates_advanced(soup2)

        # Get certificate
        response = session.get(hrefs[name][1])

        if not response:
            raise Exception("No response")
        if response.status_code != 200:
            raise Exception(f"Got non-200 status: {response.status_code}")
        if response.history:
            raise Exception(f"Redirected to {response.history[-1].url}")

        dev.write_file(response.content, f"{name}.pem")
        dev.related.files.add(f"{name}.pem")

        result[name]["file"] = f"{name}.pem"

    return {"certificates": result}
