"""
Pull the device's usage policy from /Firewall.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4.element import Tag
from bs4 import BeautifulSoup

from peat import DeviceData

from ..http import HTTP3622
from ..parse.Firewall import parse_rules


def correct_config_view(session: HTTP3622) -> str:
    response = session.get_endpoint("firewall")

    if not response:
        raise Exception("No response")
    elif response.status_code != 200:
        raise Exception("Non-200 status code")
    elif len(response.history) > 0:
        raise Exception("Redirected")

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


def pull_firewall_rules(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Corrects the Firewall view to integrate all rules into a singular list

    | Field                                   | Description                                                                        |
    |-----------------------------------------|------------------------------------------------------------------------------------|
    | `firewall`                              | Root container                                                                     |
    | `firewall.rules`                        | Contains an array of rules                                                         |
    | `firewall.rules[n].order`               | In what position is this rule?                                                     |
    | `firewall.rules[n].interface`           | To what interface does this rule apply?                                            |
    | `firewall.rules[n].name`                | Human-readable name assigned to the rule                                           |
    | `firewall.rules[n].status`              | Enabled or Disabled                                                                |
    | `firewall.rules[n].source_address`      | IP address or network from which a packet must come from to match this rule        |
    | `firewall.rules[n].source_port`         | Port number(s) to from which a packet was sent from to match this rule             |
    | `firewall.rules[n].description`         | Description provided for this rule (redundant, optional)                           |
    | `firewall.rules[n].protocol`            | The protocol to which this rule applies                                            |
    | `firewall.rules[n].action`              | What to do to the packet (ACCEPT, DROP, REJECT)                                    |
    | `firewall.rules[n].destination_address` | To which address or network a packet must be destined to match this rule           |
    | `firewall.rules[n].destination_port`    | To which port(s) a packet must be destined for to match this rule                  |
    | `firewall.drop_ping`                    | Whether ping packets to this device (or connected devices) are dropped             |
    | `firewall.drop_traceroute`              | Whether traceroute packets to this device are dropped                              |
    | `firewall.require_encryption`           | Whether packets must go through an established IPsec tunnel                        |
    | `firewall.allow_all_encrypted`          | Do not enforce firewall rules on packets going through an established IPsec tunnel |
    """
    return parse_rules(session.gen_soup(correct_config_view(session)))
