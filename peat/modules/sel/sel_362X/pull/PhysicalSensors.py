"""
Pull the device's sensors configuration from /PhysicalSensors.sel

Author: Francisco Santana
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

from ..http import HTTP362X
from ..parse.PhysicalSensors import enabled, input_contact, light_sensor, motion_sensor


def pull_physical_sensors(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration of the physical sensors page
    """

    result = {}
    response = session.get_endpoint("physical_sensors")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception("Redirected")
    if response.status_code != 200:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    try:
        result["enabled"] = enabled(soup)
    except Exception as e:
        logger.warning("Failed to get global status")
    try:
        result["input_contact"] = input_contact(soup)
    except Exception as e:
        logger.warning("Failed to get input contact status")
    try:
        result["light"] = light_sensor(soup)
    except Exception as e:
        logger.warning("Failed to get ligt sensor status")
    try:
        result["motion"] = motion_sensor(soup)
    except Exception as e:
        logger.warning("Failed to get motion sensor status")

    return {"sensors": result}
