"""
Get data from /PortMappings.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP3622
from ..parse.SerialPortProfiles import parse_profiles


def pull_serial_port_profiles(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration under /PortMappings.sel

    | Field                                         | Description                                                         |
    |-----------------------------------------------|---------------------------------------------------------------------|
    | `serial_port_profiles`                        | Root container                                                      |
    | `serial_port_profiles.[name]`                 | The name of the serial port profile                                 |
    | `serial_port_profiles.[name].baud_rate`       | The rate at which data is transmitted                               |
    | `serial_port_profiles.[name].data_bits`       | Unit of size for data                                               |
    | `serial_port_profiles.[name].parity`          | Parity algorithm (ECC)                                              |
    | `serial_port_profiles.[name].hw_flow_control` | Whether to use hardware flow control                                |
    | `serial_port_profiles.[name].interface`       | The interface to use for communicating                              |
    | `serial_port_profiles.[name].frame_size`      | The maximum size for a single frame of data                         |
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("serial_port_profiles")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_profiles(soup)

    return {"serial_port_profiles": result}
