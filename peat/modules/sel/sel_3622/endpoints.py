"""
HTTP endpoints for the SEL-3622.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from typing import Literal

AVAILABLE_ENDPOINTS = Literal[
    # Commissioning
    "commissioning",
    # Login/Dash/Logout
    "login",
    "dashboard",
    "logout",
    # System
    "usage_policy",
    "file_management",
    "web_server",
    "management_interface",
    "device_reset",
    "physical_sensors",
    # User
    "accounts",
    "ldap_settings",
    "radius_settings",
    "local_groups",
    # Network
    "network_settings",
    "static_routes",
    "syslog",
    "firewall",
    "hosts",
    "snmp_settings",
    # Serial Ports
    "serial_port_settings",
    "serial_port_profiles",
    "port_mappings",
    # Security
    "x509_certificates",
    "ipsec_connections",
    "allowed_clients",
    "ssh_host_key",
    "password_management",
    # Reports
    "system_logs",
    "diagnostics",
    "proxy_reports",
]

ENDPOINTS: dict[
    AVAILABLE_ENDPOINTS,
    str,
] = {
    # Commissioning
    "commissioning": "/Commissioning.sel",
    # Login/Dash/Logout
    "login": "/Login.sel",
    "dashboard": "/index.sel",
    "logout": "/Logout.sel",
    # System
    "usage_policy": "/UsagePolicy.sel",
    "file_management": "/FileManagement.sel",
    "web_server": "/WebServer.sel",
    "management_interface": "/ManagementInterface.sel",
    "device_reset": "/DeviceReset.sel",
    "physical_sensors": "/PhysicalSensors.sel",
    # User
    "accounts": "/Users.sel",
    "ldap_settings": "/LDAP.sel",
    "radius_settings": "/RADIUS.sel",
    "local_groups": "/LocalGroups.sel",
    # Network
    "network_settings": "/NetworkSettings.sel",
    "static_routes": "/StaticRoutes.sel",
    "syslog": "/Syslog.sel",
    "firewall": "/Firewall.sel",
    "hosts": "/Hosts.sel",
    "snmp_settings": "/SNMP.sel",
    # Serial Ports
    "serial_port_settings": "/SerialPortSettings.sel",
    "serial_port_profiles": "/SerialPortProfiles.sel",
    "port_mappings": "/PortMappings.sel",
    # Security
    "x509_certificates": "/X509.sel",
    "ipsec_connections": "/IPsec.sel",
    "allowed_clients": "/AllowedClients.sel",
    "ssh_host_key": "/SSH_Host_Key.sel",
    "password_management": "/PasswordManagement.sel",
    # Reports
    "system_logs": "/SysLogReport.sel",
    "diagnostics": "/Diagnostics.sel",
    "proxy_reports": "/ProxyReports.sel",
}

__all__ = ["ENDPOINTS", "AVAILABLE_ENDPOINTS"]
