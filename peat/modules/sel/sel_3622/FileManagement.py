"""
Get data from /FileManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from dataclasses import dataclass
from time import gmtime, strftime, time

from bs4.element import Tag

from .http import HTTP3622


@dataclass
class SystemSettings:
    hash: str
    data: bytes
    time: str


def queue_system_settings(http: HTTP3622) -> bool:
    """
    Queue the generation of the system settings file.
    """

    http.log.info("Preparing a configuration file snapshot...")

    response = http.post(
        http.endpoint("filesystem"),
        data={
            "Password": "Peater!1",
            "PasswordConfirm": "Peater!1",
            "submit": "Generate",
        },
    )

    if not response:
        http.log.error("No response")
        return False

    if response.status_code != 200:
        http.log.error("Could not query setting file creation")
        return False

    soup = http.gen_soup(response.text)
    message = soup.find("div", {"id": "formMessage"})

    if (
        not isinstance(message, Tag)
        or "System Settings file is being generated." not in message.get_text()
    ):
        http.log.error("Could not initiate settings file generation")
        return False

    http.log.info("Sent a generation request.")

    # TODO: find a suitable way of awaiting the completion of this task.
    # Threading?

    return True


def query_system_settings(http: HTTP3622) -> SystemSettings | None:
    """
    Query the status of the system settings file.

    Will download it if it is ready.
    """

    response = http.post(
        http.endpoint("filesystem"),
        data={"Password": None, "PasswordConfirm": None, "submit": "Export"},
        headers={"Referrer": http.endpoint("filesystem")},
    )

    if not response:
        http.log.error("No response")
        return None

    if response.status_code != 200:
        http.log.error("Could not pull file")
        return None

    raise NotImplementedError()


__all__ = ["queue_system_settings", "query_system_settings", "SystemSettings"]
