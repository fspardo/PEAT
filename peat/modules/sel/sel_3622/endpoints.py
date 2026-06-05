"""
HTTP endpoints for the SEL-3622.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Literal

AVAILABLE_ENDPOINTS = Literal[
    "commissioning",
    "login",
    "dashboard",
    "users",
    "logout",
    "webserver",
    "management",
    "pam",
    "filesystem",
    "reset",
    "diagnostics",
    "syslog",
    "help",
    "cert",
    "cert_import",
    "confirm_deletion",
]

ENDPOINTS: dict[
    AVAILABLE_ENDPOINTS,
    str,
] = {
    "commissioning": "/Commissioning.sel",
    "login": "/Login.sel",
    "dashboard": "/index.sel",
    "users": "/Users.sel",
    "logout": "/Logout.sel",
    "webserver": "/WebServer.sel",
    "management": "/ManagementInterface.sel",
    "pam": "/PasswordManagement.sel",
    "filesystem": "/FileManagement.sel",
    "reset": "/DeviceReset.sel",
    "diagnostics": "/Diagnostics.sel",
    "syslog": "/SysLogReport.sel",
    "help": "/Help.sel",
    "cert": "/X509.sel",
    "cert_import": "/X509_Import.sel",
    "confirm_deletion": "/ConfirmDeletion.sel",
}

__all__ = ["ENDPOINTS", "AVAILABLE_ENDPOINTS"]
