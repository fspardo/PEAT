"""
Parse the device's sensors configuration from /PhysicalSensors.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import Tag

from peat import DeviceData

def get_input_value(s: BeautifulSoup, type: Literal["checkbox", "text"], id: str) -> str:
    """
    Get the value of an input field based on its type and ID.
    """

    field = s.find("input", {"type": type, "id": id})
    if not isinstance(field, Tag):
        raise Exception("Could not find field")
    return field.attrs["value"]


def get_radio_value(s: BeautifulSoup, name: str) -> str:
    """
    Get the value of a radio field based on its name
    """

    field = s.find("input", {"type": "radio", "name": name, "checked": ""})
    if not isinstance(field, Tag):
        raise Exception("Could not find field")
    return field.attrs["value"]


def enabled(s: BeautifulSoup) -> str:
    """
    Get if the physical sensors are globally enabled
    """

    return get_input_value(s, "checkbox", "g_enable")


def input_contact(s: BeautifulSoup) -> dict[str, Any]:
    """
    Get the configuration of the input contacts (front pair of wire grips)
    """

    # TODO: extract most recent events
    # NOTE: the sample device seems to have broken sensors
    ic_current_state = s.find("td", {"id": "ic_current_state"})
    if not isinstance(ic_current_state, Tag):
        raise Exception("Could not get field")

    return {
        "enabled": get_input_value(s, "checkbox", "ic_enable"),
        "on_msg": get_input_value(s, "text", "ic_syslog_energized"),
        "off_msg": get_input_value(s, "text", "ic_syslog_deenergized"),
        "state": ic_current_state.get_text(strip=True).removeprefix("Current State: "),
    }


def light_sensor(s: BeautifulSoup) -> dict[str, Any]:
    """
    Get the configuration of the light sensor (hole to the right of the SEL logo)
    """

    # TODO: extract most recent events
    # NOTE: the sample device seems to have broken sensors
    LS_MAP = ["High", "Medium", "Low"]

    sensitivity = get_radio_value(s, "ls_sensitivity_id")
    if not sensitivity.isnumeric():  # Ensure it is numeric (prevent breakage)
        sensitivity = "UNKNOWN"
    else:  # Parse and check range
        sensitivity = int(sensitivity)
        if sensitivity >= 1 and sensitivity <= 3:
            sensitivity = "UNKNOWN"
        else:  # Convert to human-readable string
            sensitivity = LS_MAP[int(sensitivity)]

    return {
        "enabled": get_input_value(s, "checkbox", "ls_enable"),
        "sensitivity": sensitivity,
    }


def motion_sensor(s: BeautifulSoup) -> dict[str, Any]:
    """
    Get the configuration of the motion sensor (detects jostling and tilting)
    """

    # TODO: extract most recent events
    # NOTE: the sample device seems to have broken sensors
    ACCEL_MAP = ["Tilt Only", "Impact and Tilt"]

    sensitivity = get_radio_value(s, "accelerometer_sensitivity_id")
    if not sensitivity.isnumeric():  # Ensure it is numeric (prevent breakage)
        sensitivity = "UNKNOWN"
    else:  # Parse and check range
        sensitivity = int(sensitivity)
        if sensitivity >= 1 and sensitivity <= 3:
            sensitivity = "UNKNOWN"
        else:  # Convert to human-readable string
            sensitivity = ACCEL_MAP[int(sensitivity)]

    return {
        "enabled": get_input_value(s, "checkbox", "accel_enable"),
        "sensitivity": sensitivity,
    }