"""
Parse data from /X509.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

BASIC_DATA = {
    "name": "name",
    "country": "country",
    "is_ca": "ca",
    "valid_start": "start",
    "valid_end": "end",
    "oscp_uri": "ocsp",
}

ADVANCED_DATA = {
    "version": "version",
    "serial_number": "serial_number",
    "name": "name",
    "subject_alt_names": "subject_alt_name",
    "subject": "distinguished_name",
    "country": "country",
    "state": "state",
    "locality": "locality",
    "org_name": "organization_name",
    "org_unit_name": "organization_unit_name",
    "common_name": "common_name",
    "email": "email_addr",
    "issuer_subject": "issuer_dn",
    "issuer_country": "issuer_country",
    "issuer_state": "issuer_state",
    "issuer_locality": "issuer_locality",
    "issuer_org_name": "issuer_organization_name",
    "issuer_org_unit_name": "issuer_organization_unit_name",
    "issuer_common_name": "issuer_common_name",
    "issuer_email": "issuer_email_addr",
    "valid_start": "valid_start",
    "valid_end": "valid_end",
    "is_ca": "is_ca",
    "ocsp_uri": "ocsp_uri",
    "rsa_key": "rsa_key",
}


def parse_certificates_advanced(soup: BeautifulSoup) -> dict[str, Any]:
    """More advanced parsing for more advanced data"""
    result = {}

    for k in ADVANCED_DATA:
        d = soup.find("label", {"id": ADVANCED_DATA[k]})
        assert isinstance(d, Tag)
        result[k] = d.get_text("", True)

    return result


def parse_certificates_basic(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    table = soup.find("table", {"id": "x509List"})
    assert isinstance(table, Tag)

    rows = table.find_all("tr", {"class": ["odd", "even"]})

    for row in rows:
        x = {}
        assert isinstance(row, Tag)

        for k in BASIC_DATA:
            a = row.find("td", {"class": f"x509_{BASIC_DATA[k]}"})
            assert isinstance(a, Tag)
            x[k] = a.get_text("", True)

        name = x["name"]
        del x["name"]
        result[name] = x

    return result
