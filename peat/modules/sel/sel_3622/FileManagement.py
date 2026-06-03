"""
Get data from /FileManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from copy import copy
from dataclasses import dataclass
from time import gmtime, strftime, time
from typing import Any, Final

from bs4.element import Tag

from .endpoints import ENDPOINTS
from .http import HTTP3622

HASH_ID: Final[str] = "display_systemSettingsExportHash"
FORM_CONTENT: Final[dict[str, Any]] = {
    "fileUploadType": (None, "firmwareFile"),
    "JAVASCRIPT": (None, "True"),
    "MAX_FILE_SIZE": (None, "125000000"),
    "t": (None, ""),
    "uploadedfile": (None, ""),
    "ImportPassword": (None, ""),
    "Password": (None, ""),
    "PasswordConfirm": (None, ""),
    "submit": (None, ""),
}


def form_generate(password: str, token: str):
    """
    Create a form populated with the requisite "Generate" data
    """
    result = copy(FORM_CONTENT)
    result["Password"] = (None, password)
    result["PasswordConfirm"] = (None, password)
    result["t"] = (None, token)
    result["submit"] = (None, "Generate")

    return result


def form_export(token: str):
    """
    Create a form populated with the requisite "Generate" data
    """
    result = copy(FORM_CONTENT)
    result["t"] = (None, token)
    result["submit"] = (None, "Export")

    return result


@dataclass
class SystemSettings:
    hash: str
    data: bytes
    time: str


def pull_requesite_data(http: HTTP3622) -> tuple[str, str] | None:
    response = http.get(ENDPOINTS["filesystem"], use_cache=False)

    if not response:
        http.log.error("No response")
        return None

    if response.status_code != 200:
        http.log.error("Error loading page")
        return None

    soup = http.gen_soup(response.text)

    old_hash = soup.find("span", {"id": HASH_ID})

    if not isinstance(old_hash, Tag):
        http.log.error("Could not get old hash log")
        return None

    token = soup.find("input", {"type": "hidden", "id": "t"})

    if not isinstance(token, Tag):
        http.log.error("Could not get token")
        return None

    return old_hash.get_text(strip=True), token.attrs["value"]


class SystemSettingsPoller:
    """
    Handles queueing and polling the system settings file
    """

    http: HTTP3622
    old_hash: str
    token: str

    def __init__(self, http: HTTP3622):
        self.http = http
        self.old_hash = ""
        self.token = ""

    def queue(self) -> bool:
        """
        Queue the generation of the system settings file.
        """

        self.http.log.info("Preparing a configuration file snapshot...")

        pair = pull_requesite_data(self.http)

        if not pair:
            return False

        old_hash, self.token = pair

        self.http.log.debug(f"Old hash: {old_hash}; token: {self.token}")

        response = self.http.post(
            self.http.endpoint("filesystem"),
            files=form_generate("Peater!1", self.token),
            headers={"Referer": f"https://{self.http.ip}/{ENDPOINTS['filesystem']}"},
        )

        if not response:
            self.http.log.error("No response")
            return False

        if response.status_code != 200:
            self.http.log.error("Could not query setting file creation")
            return False

        soup = self.http.gen_soup(response.text)
        message = soup.find("div", {"id": "formMessage"})

        if (
            not isinstance(message, Tag)
            or "System Settings file is being generated. This may take a few minutes."
            not in message.get_text()
        ):
            self.http.log.error("Could not initiate settings file generation")
            return False

        self.http.log.info("Sent a generation request.")
        self.old_hash = old_hash

        return True

    def query(self) -> SystemSettings | None:
        """
        Query the status of the system settings file.

        Will download it if it is ready. Returns `None` if it's not ready.
        """

        if self.old_hash == "" or self.token == "":
            self.http.log.error("Settings not queued!")
            return None

        response = self.http.post(
            self.http.endpoint("filesystem"),
            files=form_export(self.token),
            headers={"Referrer": f"https://{self.http.ip}/{ENDPOINTS['filesystem']}"},
        )

        if not response:
            self.http.log.error("No response")
            return None

        if response.status_code != 200:
            self.http.log.error("Could not pull file")
            return None

        raise NotImplementedError()


__all__ = ["SystemSettingsPoller", "SystemSettings"]
