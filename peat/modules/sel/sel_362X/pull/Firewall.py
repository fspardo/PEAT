"""
Pull the device's usage policy from /Firewall.sel

Author: Francisco Santana
"""

from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData

from ..http import HTTP362X
from ..parse.Firewall import parse_rules


def correct_config_view(session: HTTP362X) -> str:
    response = session.get_endpoint("firewall")

    if not response:
        raise Exception("No response")
    elif response.status_code != 200:
        raise Exception("Non-200 status code")
    elif len(response.history) > 0:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    keys = [
        "dropPing",
        "dropTraceroute",
        "mustBeEncrypted",
        "allowAllEncrypted",
        "textOnly",
        "integrated",
        "t",
    ]

    def getinpt(soup: BeautifulSoup, k: str) -> str:
        v = soup.find("input", {"id": k})
        assert isinstance(v, Tag)
        v = v.get("value")
        assert isinstance(v, str)
        return v

    cfg = {k: getinpt(soup, k) for k in keys}

    for k in keys:
        if cfg[k] == "false":
            del cfg[k]

    cfg["FirewallRuleId"] = ""
    cfg["textOnly"] = "true"
    cfg["integrated"] = "true"
    cfg["submit"] = "Save"

    resp = session.post_endpoint("firewall", data=cfg)
    assert resp and resp.status_code == 200 and len(resp.history) == 0

    return resp.text


def pull_firewall_rules(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Corrects the Firewall view to integrate all rules into a singular list
    """
    return {"firewall": parse_rules(session.gen_soup(correct_config_view(session)))}
