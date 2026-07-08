"""
Get data from /SerialPortSettings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.SerialPortSettings import parse_settings


def pull_serial_port_settings(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel

    | Field                             | Description                                                         |
    |-----------------------------------|---------------------------------------------------------------------|
    | `serial_ports`                    | Root container                                                      |
    | `serial_ports[i].state`           | "Enabled" if enabled, "Disabled" if disabled, "Unknown" otherwise   |
    | `serial_ports[i].profile`         | The profile being used for this port (listed under "Port Profiles") |
    | `serial_ports[i].baud_rate`       | The baud (data transmission) rate                                   |
    | `serial_ports[i].data_bits`       | The number of bits of data transmitted per unit                     |
    | `serial_ports[i].parity`          | The parity algorithm being used for this port                       |
    | `serial_ports[i].stop_bits`       |                                                                     |
    | `serial_ports[i].hw_flow_control` | Whether hardware flow control is enabled for this port              |
    | `serial_ports[i].interface`       | The communications interface being used for this port               |
    | `serial_ports[i].alias`           | Human-readable name for the interface                               |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("serial_port_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_settings(soup)

    return {"serial_ports": result}
