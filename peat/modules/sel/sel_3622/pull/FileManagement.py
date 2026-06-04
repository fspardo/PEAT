"""
Get data from /FileManagement.sel.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from copy import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final

from bs4.element import Tag

from peat import log
from peat.data.models import DeviceData

from ..endpoints import ENDPOINTS
from ..http import HTTP3622

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
    # Fields to do with system settings
    prev_hash: str
    hash: str
    password: str
    data: bytes
    time: str
    file_name: str

    # Fields to do with the firmware version
    current_firmware: str
    previous_firmware: str

    # TODO: pull hash for last uploaded config and connection directory


def pull_hash_and_token(http: HTTP3622) -> dict[str, str] | None:
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
        http.log.error("Could not get old hash")
        return None

    token = soup.find("input", {"type": "hidden", "id": "t"})

    if not isinstance(token, Tag):
        http.log.error("Could not get token")
        return None

    current_version = soup.find("span", {"id": "display_CurrentVersion"})

    if not isinstance(current_version, Tag):
        http.log.error("Could not get current version")
        return None

    previous_version = soup.find("span", {"id": "display_PreviousVersion"})

    pv = "Unknown"
    if isinstance(previous_version, Tag):
        pv = previous_version.get_text(strip=True)

    return {
        "old_hash": old_hash.get_text(strip=True),
        "token": token.attrs["value"],
        "current_version": current_version.get_text(strip=True),
        "previous_version": pv,
    }


def pull_hash(http: HTTP3622) -> str | None:
    response = http.get(ENDPOINTS["filesystem"], use_cache=False)

    if not response:
        http.log.error("No response")
        return None

    if response.status_code != 200:
        http.log.error("Error loading page")
        return None

    soup = http.gen_soup(response.text)

    hash = soup.find("span", {"id": HASH_ID})

    if not isinstance(hash, Tag):
        http.log.error("Could not get old hash log")
        return None

    return hash.get_text(strip=True)


def get_password():
    return "Peat!123"


class SystemSettingsPoller:
    """
    Handles queueing and polling the system settings file
    """

    http: HTTP3622
    old_hash: str
    token: str
    password: str
    current_version: str
    previous_version: str

    def __init__(self, http: HTTP3622):
        self.http = http
        self.old_hash = ""
        self.token = ""
        self.password = ""
        self.current_version = ""
        self.previous_version = ""

    def queue(self) -> bool:
        """
        Queue the generation of the system settings file.
        """

        self.http.log.info("Preparing a configuration file snapshot...")

        info = pull_hash_and_token(self.http)

        if not info:
            return False

        old_hash, self.token = info["old_hash"], info["token"]

        self.http.log.debug(f"Old hash: {old_hash}; token: {self.token}")

        password = get_password()

        response = self.http.post(
            self.http.endpoint("filesystem"),
            files=form_generate(password, self.token),
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

        self.http.log.info(
            f'Sent a generation request; the file will be encrypted with the password, "{password}"'
        )
        self.old_hash = old_hash
        self.password = password
        self.current_version = info["current_version"]
        self.previous_version = info["previous_version"]

        return True

    def query(self, force: bool = False) -> SystemSettings | bool:
        """
        Query the status of the system settings file.

        Will download it if it is ready. Returns `True` if it's not ready and `False` on error.

        NOTE: Since the SHA-1 hash generated by the device relies on the unencrypted configuration,
        pass `force=true` to this function
        """

        if self.old_hash == "" or self.token == "":
            self.http.log.error("Settings not queued!")
            return False

        hash = pull_hash(self.http)

        if not force and hash == self.old_hash:
            self.http.log.debug("No change to hash")
            return True

        response = self.http.post(
            self.http.endpoint("filesystem"),
            files=form_export(self.token),
            headers={"Referrer": f"https://{self.http.ip}/{ENDPOINTS['filesystem']}"},
        )

        if not response:
            self.http.log.error("No response")
            return False

        if response.status_code != 200:
            self.http.log.error("Could not pull file")
            return False

        if response.headers["Content-Type"] == "text/html":
            self.http.log.error("Incorrect content type")
            return False

        if hash is None:
            self.http.log.error("Could not pull hash")
            return False

        gen_time = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}"

        assert isinstance(response.content, bytes)

        return SystemSettings(
            self.old_hash,
            hash,
            self.password,
            response.content,
            gen_time,
            f"SystemSettings-{gen_time}.bkp",
            self.current_version,
            self.previous_version,
        )


def pull_file_management(dev: DeviceData, http: HTTP3622) -> dict[str, Any]:
    ssp = SystemSettingsPoller(http)
    if not ssp.queue():
        raise Exception("Failed to queue system file generation")

    # Query once every 30 seconds, for a total of 300s (5m).
    for i in range(0, 10):
        log.debug(f"Query {i + 1} of 10...")
        from time import sleep

        sleep(10)
        sys_settings = ssp.query()
        if isinstance(sys_settings, SystemSettings):
            log.info("Pulled system configuration backup")
            break

        if not sys_settings:
            raise Exception("Error in querying system settings")

    if not isinstance(sys_settings, SystemSettings):
        log.info("Pulling system configuration backup...")
        sys_settings = ssp.query(force=True)
        if not isinstance(sys_settings, SystemSettings):
            raise Exception("Failed to pull the system configuration backup")

    log.info(f"Pulled system configuration (saved as {sys_settings.file_name})")

    dev.write_file(sys_settings.data, sys_settings.file_name)
    dev.related.files.add(sys_settings.file_name)

    return {
        "system_settings_backup": {
            "old_hash": sys_settings.prev_hash,
            "new_hash": sys_settings.hash,
            "file_name": sys_settings.file_name,
            "config_archive": sys_settings.data,
            "password": sys_settings.password,
            "time_pulled": sys_settings.time,
        },
        "firmware": {
            "current_version": sys_settings.current_firmware,
            "previous_version": sys_settings.previous_firmware,
        },
    }


__all__ = ["SystemSettingsPoller", "SystemSettings", "pull_file_management"]
