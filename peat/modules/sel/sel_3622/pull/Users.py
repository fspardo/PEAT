"""
Pull the device's users from /Users.sel

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Any

from bs4.element import Tag

from peat import DeviceData

from ..endpoints import ENDPOINTS
from ..http import HTTP3622

def pull_usage_policy(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    result = {}

    

    return result