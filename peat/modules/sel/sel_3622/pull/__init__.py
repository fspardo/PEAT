"""
Pull methods for different endpoints.

Ideally, scripts involved in pulling data from the device should go
in this directory, and a singular function that returns a dictionary
should be exported from each module.

The prototype of each function should be:
    (dev: DeviceData, session: HTTP3622) -> dict[str, Any]

Raise exceptions where the pull fails.

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

# System

from .UsagePolicy import pull_usage_policy
from .FileManagement import pull_file_management
from .PhysicalSensors import pull_physical_sensors

# User
# Network
from .NetworkSettings import pull_network_settings
from .StaticRoutes import pull_static_routes

# Serial Ports


# Security


# Reports
