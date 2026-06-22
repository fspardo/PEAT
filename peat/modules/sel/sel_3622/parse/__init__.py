# ruff: noqa: I001
"""
Parse methods for different endpoints.

Ideally, scripts involved in parsing data from the device should go
in this directory, and a singular function that returns a dictionary
should be exported from each module.

The first argument is the device's data, which may be used as an aid
to get information. The second argument is the directory containing
the pulled data.

The prototype of each function should be:
    (dev: DeviceData, path: Path) -> dict[str, Any]

Raise exceptions where the parse fails.

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

# Sorting has been disabled to make imports match the ordering of the UI on the SEL

# System

# User
from .Users import parse_users

# Network

# Serial Ports

# Security

# Reports
