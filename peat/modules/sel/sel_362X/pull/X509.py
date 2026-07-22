"""
Get data from /X509.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.X509 import parse_certificates_advanced, parse_certificates_basic


def pull_certificates(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /X509.sel

    Entries with an asterisk are included with a basic parse. All others must be retrieved from an advanced parse.

    | Field                                         | Description                                                         |
    |-----------------------------------------------|---------------------------------------------------------------------|
    | `certificates`                                | Root container                                                      |
    | `certificates.[name]`                         | Information about a certificate of that name                        |
    | `certificates.[name].version`               * | Certificate version                                                 |
    | `certificates.[name].serial_number`           | Certificate serial number                                           |
    | `certificates.[name].name`                    | The name of the certificate (friendly name)                         |
    | `certificates.[name].subject_alt_names`       | Alternative names for the subject                                   |
    | `certificates.[name].subject`                 | The subject to which this certificate is issued                     |
    | `certificates.[name].country`               * | Subject country of origin                                           |
    | `certificates.[name].state`                   | Subject state of origin (in the US)                                 |
    | `certificates.[name].locality`                | Subject locality (city)                                             |
    | `certificates.[name].org_name`                | Subject organization                                                |
    | `certificates.[name].org_unit_name`           | Subject organization unit                                           |
    | `certificates.[name].common_name`             | Subject common name                                                 |
    | `certificates.[name].email`                   | Subject email                                                       |
    | `certificates.[name].issuer_subject`          | The issuer from which this certificate was signed                   |
    | `certificates.[name].issuer_country`          | Issuer country of origin                                            |
    | `certificates.[name].issuer_state`            | Issuer state of origin (in the US)                                  |
    | `certificates.[name].issuer_locality`         | Issuer locality (city)                                              |
    | `certificates.[name].issuer_org_name`         | Issuer organization                                                 |
    | `certificates.[name].issuer_org_unit_name`    | Issuer organization unit                                            |
    | `certificates.[name].issuer_common_name`      | Issuer common name                                                  |
    | `certificates.[name].issuer_email`            | Issuer email                                                        |
    | `certificates.[name].valid_start`           * | Certificate valid start date                                        |
    | `certificates.[name].valid_end`             * | Certificate valid end date                                          |
    | `certificates.[name].is_ca`                 * | Whether this certificate is an authority                            |
    | `certificates.[name].ocsp_uri`              * | Where the certificate's revocation lists may be downloaded          |
    | `certificates.[name].rsa_key`                 | Whether this certificate uses an RSA key                            |
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
