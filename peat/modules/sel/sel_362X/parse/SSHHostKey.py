"""
Parse data from /SSHHostKey.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

FORMS = {
    "dsa_pubkey": "pubSSH",
    "rsa_pubkey": "pubRSA",
}


def parse_host_keys(soup: BeautifulSoup) -> dict[str, Any]:
    """Performs a basic parse of the table contents in the main page"""
    result = {}

    for f in FORMS:
        form = soup.find("form", {"id": FORMS[f]})
        assert isinstance(form, Tag)
        pre = form.find("pre")
        assert isinstance(pre, Tag)

        result[f] = pre.get_text("\n", True)

    return result
