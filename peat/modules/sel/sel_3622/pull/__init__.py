# ruff: noqa: I001
"""
Pull methods for different endpoints.

Ideally, scripts involved in pulling data from the device should go
in this directory, and a singular function that returns a dictionary
should be exported from each module.

Each function should return a dictionary containing the configuration of
the designated endpoint.

The prototype of each function should be:
    (dev: DeviceData, session: HTTP3622) -> dict[str, Any]

Raise exceptions where the pull fails.

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

# Sorting has been disabled to make imports match the ordering of the UI on the SEL

# System
from .UsagePolicy import pull_usage_policy
from .FileManagement import pull_file_management, initialize_file_management_pull
from .PhysicalSensors import pull_physical_sensors

# User
from .Users import pull_users
from .LDAP import pull_ldap_settings
from .RADIUS import pull_radius_settings
from .LocalGroups import pull_local_groups

# Network
from .NetworkSettings import pull_network_settings
from .StaticRoutes import pull_static_routes
from .Syslog import pull_syslog_settings
from .Firewall import pull_firewall_rules
from .Hosts import pull_hosts
from .SNMP import pull_snmp_settings

# Serial Ports
from .SerialPortSettings import pull_serial_port_settings
from .SerialPortProfiles import pull_serial_port_profiles
from .PortMappings import pull_port_mappings

# Security
from .X509 import pull_certificates

# Reports
