"""
Pull the device's usage policy from /UsagePolicy.sel

Author: Francisco Santana
"""

from typing import Any

from bs4.element import Tag

from peat import DeviceData

from ..endpoints import ENDPOINTS
from ..http import HTTP3622


def pull_usage_policy(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    response = session.get_endpoint("usage_policy")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception("Redirected")
    if response.status_code != 200:
        raise Exception("Non-200 status code")

    soup = session.gen_soup(response.text)

    textarea = soup.find("textarea", {"id": "UseBanner"})
    if not isinstance(textarea, Tag):
        raise Exception("Could not find text area")

    return {"usage_policy": textarea.get_text(strip=True)}
