"""
Parse data from /SSHHostKey.sel.

Author: Francisco Santana
"""

from pathlib import Path
from typing import Any, Final

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

from .helper import *

FORMS = {
    "dsa_pubkey": "pubSSH",
    "rsa_pubkey": "pubRSA",
}


def parse_host_keys(soup: BeautifulSoup) -> dict[str, Any]:
    """Read the public keys on this system"""
    result = {f: get_text_of(find_tag_f(soup, "form", {"id": FORMS[f]}), "pre") for f in FORMS}

    return result
