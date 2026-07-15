"""
Pull the device's sensors configuration from /PhysicalSensors.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData

from ..http import HTTP3622
from ..parse.PhysicalSensors import enabled, input_contact, light_sensor, motion_sensor


def pull_physical_sensors(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull the configuration of the physical sensors page

    | Field                   | Description                                          |
    |-------------------------|------------------------------------------------------|
    | `sensors.enabled`       | Whether the sensors are enabled                      |
    | `sensors.input_contact` | Whether the Input Contact sensor is enabled          |
    | `sensors.light`         | Whether the Light sensor is enabled                  |
    | `sensors.motion`        | Whether the Motion sensor (accelerometer) is enabled |

    """

    result = {}
    response = session.get_endpoint("physical_sensors")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception("Redirected")
    if response.status_code != 200:
        raise Exception("Non-200 status code")

    soup = session.gen_soup(response.text)

    result["enabled"] = enabled(soup)
    result["input_contact"] = input_contact(soup)
    result["light"] = light_sensor(soup)
    result["motion"] = motion_sensor(soup)

    return {"sensors": result}
