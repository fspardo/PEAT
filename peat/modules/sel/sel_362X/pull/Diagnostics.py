"""
Extract data from the /Diagnostics.sel endpoint

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.Diagnostics import parse_diagnostics_3622_R200


def pull_diagnostics(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /Diagnostics.sel

    | Field                                 | Description                    |
    |---------------------------------------|--------------------------------|
    | `diagnostics`                         | Root container                 |
    | `diagnostics.firewall_state`          | Firewall state information     |
    | `diagnostics.network_state`           | Network adapter configuration  |
    | `diagnostics.route_table_state`       | Route table information        |
    | `diagnostics.hard_drive_usage`        | Hard drive usage               |
    | `diagnostics.process_list`            | Process list                   |
    | `diagnostics.available_entropy`       | Entropy                        |
    | `diagnostics.ipsec_config`            | IPsec config file              |
    | `diagnostics.ipsec_state`             | IPsec state                    |
    | `diagnostics.ipsec_policy`            | IPsec policy                   |
    | `diagnostics.ipsec_status`            | IPsec status                   |
    | `diagnostics.ipsec_total`             | IPsec statistics               |
    | `diagnostics.free_memory`             | Memory information             |
    | `diagnostics.hardware_offload_events` | Hardware offloads              |
    | `diagnostics.selinux_audit_failures`  | Audit failures                 |
    | `diagnostics.selinux`                 | SELinux status                 |
    | `diagnostics.autoscopy_status`        | Autoscopy status               |
    | `diagnostics.whitelist`               | Whitelist status               |
    """

    response = session.get_endpoint("diagnostics")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"diagnostics": parse_diagnostics_3622_R200(session.gen_soup(response.text))}
