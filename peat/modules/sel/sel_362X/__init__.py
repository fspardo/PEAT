"""
SEL-362X Family of Security Gateways.

This module is designed to support both the SEL-3622 and the SEL-3620, though
was originally developed for the former.

Authors:
    - Francisco Santana
    - Nehal Ameen
"""

from time import sleep

from peat import DeviceData, DeviceModule, IPMethod, exit_handler, Service

from .sel362x_http import HTTP362X
from . import sel362x_pull as p

from types import FunctionType
from typing import Any, Optional
from pydantic import BaseModel
from copy import deepcopy as clone


def webcfg_summarize(dev: DeviceData, data: dict[str, Any]):
    """Summarize the contents of the full web config."""
    if "users" in data:
        for username in data["users"]:
            dev.related.user.add(username)

    if "network" in data:
        for addr in data["network"]["addresses"]:
            dev.related.ip.add(addr)
        if "hostname" in data["network"]["global"]:
            dev.related.hosts.add(data["network"]["global"]["hostname"])

    if "web_server" in data:
        port = data["web_server"]["port"]
        for listener in data["web_server"]["listeners"]:
            dev.service.append(
                Service(
                    port=port,
                    protocol="https",
                    transport="tcp",
                    listen_address=listener["ip"],
                )
            )
    pass


class AdvancedRange(BaseModel):
    """An inclusive range type for versioning."""

    low: Optional[int] = None
    high: Optional[int] = None

    def __contains__(self, value: int) -> bool:
        result = True

        if self.low is not None:
            result = value >= self.low
        if self.high is not None and result:
            result = self.high >= value

        return result

    def __str__(self) -> str:
        if self.low is not None and self.high is not None:
            return f"{self.low} - {self.high}"
        elif self.low is not None:
            return f">= {self.low}"
        elif self.high is not None:
            return f"<= {self.high}"
        else:
            return "any"


AR = AdvancedRange


def irange(low: int | None = None, high: int | None = None) -> AdvancedRange:
    return AdvancedRange(low=low, high=high)


class Method:
    """Handles methods and compatibility"""

    handler: FunctionType
    attempts: int
    for_device: list[str]
    for_firmware: AdvancedRange | int

    def __init__(
        self,
        handler: FunctionType,
        attempts: int = 3,
        for_device: list[str] = [],
        for_firmware: AdvancedRange | int = AdvancedRange(),
    ):
        self.handler = handler
        self.attempts = attempts
        self.for_device = [d.lower() for d in for_device]
        self.for_firmware = for_firmware

    def dev_compat(self, dev: str) -> bool:
        """Check for device compatibility"""
        return len(self.for_device) == 0 or dev.lower() in self.for_device

    def firmware_compat(self, fw: int) -> bool:
        """Check for firmware compatibility"""
        return (
            fw in self.for_firmware
            if isinstance(self.for_firmware, AdvancedRange)
            else fw == self.for_firmware
        )

    def is_compat(self, dev: DeviceData) -> bool:
        """Check for compatibility"""
        return self.dev_compat(dev._cache["DEVICE"]) and self.firmware_compat(
            dev._cache["VERSION"]
        )

    def handle(self, dev: DeviceData, session: HTTP362X) -> dict[str, Any] | None:
        """Handle this method. Performs a compatibility check before executing the encapsulated method."""
        if not self.is_compat(dev):
            return None

        ex: Exception | None = None
        for a in range(self.attempts):
            try:
                return self.handler(dev, session)
            except Exception as e:
                ex = e

        raise (
            ex
            if isinstance(ex, Exception)
            else Exception(f"Failed to run method {self.handler.__name__}")
        )


class SEL362X(DeviceModule):
    """
    SEL-3620 Security Gateway
    SEL-3622 Ethernet Security Gateway.
    """

    device_type = "Gateway"
    vendor_id = "SEL"
    vendor_name = "Schweitzer Engineering Laboratories"
    brand = "SEL"
    module_aliases = ["sel-3622", "sel-362x", "3622", "362x"]
    default_options = {"web": {"user": "admin", "pass": "Admin123!", "users": []}}

    @classmethod
    def get_session(cls, dev: DeviceData) -> HTTP362X | None:
        """
        Get the session associated with the device
        """
        if "web_session" in dev._cache:
            session = dev._cache["web_session"]
            assert isinstance(session, HTTP362X)
            if session.is_logged_in():
                return session

        port = dev.options["https"]["port"]
        timeout = dev.options["https"]["timeout"]

        cls.log.debug(f"Verifying on port {port} with timeout {timeout}")

        session = HTTP362X(dev.ip, port, timeout)

        user = None
        passwd = None

        if dev._cache.get("verified_web_user") and dev._cache.get("verified_web_pass"):
            user = dev._cache["verified_web_user"]
            passwd = dev._cache["verified_web_pass"]
        else:
            if dev.options["web"]["user"]:
                user = dev.options["web"]["user"]
                passwd = dev.options["web"]["pass"]
            else:
                user = cls.default_options["web"]["user"]
                passwd = cls.default_options["web"]["pass"]

        cls.log.debug(f"Attempting log-in as {user}/{passwd}")
        if not session.login(str(user), str(passwd)):
            cls.log.error("Failed to log in to the device!")
            return None
        else:
            dev._cache["web_session"] = session
            dev._cache["global_token"] = session.get_global_token_value()
            return session

    @classmethod
    def _verify_http(cls, dev: DeviceData) -> bool:
        """
        Validate that the device is an SEL-362X via its HTTPS web interface
        """
        cls.log.info(f"SEL/362X: Verifying {dev.ip} via HTTPS")

        session = cls.get_session(dev)
        if not session:
            cls.log.error("Failed to log in to the device!")
            return False

        if session.validate_fid():
            cls.log.info("Success! This device is a supported SEL security gateway!")
        else:
            cls.log.error("Failure!")
            return False

        return True

    @classmethod
    def _pull(cls, dev: DeviceData) -> bool:
        """
        Pull data from the SEL 362X
        """
        cls.log.info(f"SEL/362X: Pulling information")

        session = cls.get_session(dev)
        port = dev.options["https"]["port"]
        if not session:
            cls.log.error("Failed to initialize session")
            return False

        fid = session.get_fid()
        if fid is None:
            raise Exception("Could not get the device's FID")
        fid = fid.split("-")
        device = f"{fid[0]}-{fid[1]}"
        version = int(fid[2][1:])

        dev._cache["DEVICE"] = device
        dev._cache["VERSION"] = version

        methods = [  # List pull methods here ((dev: DeviceData, session) -> dict[str, Any])
            # Prepare for pull later
            Method(p.initialize_file_management_pull, 1, for_firmware=AR(high=200)),
            # System
            Method(p.pull_usage_policy, 3),
            Method(p.pull_web_server_config, 3),
            # pull_file_management [moved to the end]
            Method(p.pull_physical_sensors, 3),
            # User
            Method(p.pull_users, 3),
            Method(p.pull_ldap_settings, 3),
            Method(p.pull_radius_settings, 3),
            Method(p.pull_local_groups, 3),
            # Network
            Method(p.pull_network_settings, 3),
            Method(p.pull_static_routes, 3),
            Method(p.pull_syslog_settings, 3),
            Method(p.pull_firewall_rules, 3),
            Method(p.pull_nat_config, 3, [], AR(low=212)),
            Method(p.pull_hosts, 3),
            Method(p.pull_snmp_settings, 3),
            # Serial Ports
            Method(p.pull_serial_port_settings, 3),
            Method(p.pull_serial_port_profiles, 3),
            Method(p.pull_port_mappings, 3),
            # Security
            Method(p.pull_certificates, 3),
            Method(p.pull_ipsec_connections, 3),
            Method(p.pull_clients, 3),
            Method(p.pull_host_keys, 3),
            Method(p.pull_passwd_mgmt, 3),
            # Reports
            Method(p.pull_syslog_report, 3),
            Method(p.pull_diagnostics, 3),
            # File Management is last to allow for enough time to see an update to the configuration
            Method(p.pull_file_management, 1, for_firmware=AR(high=200)),
        ]
        pulled_config = {}
        used_methods = {}

        tried_methods = 0

        for method in methods:
            tried_methods += 1
            cls.log.info(
                f'({tried_methods}/{len(methods)}) Attempting method "{method.handler.__name__}" for {dev.ip}:{port}'
            )

            try:
                # Call the method (`.handle()` checks for compatibility)
                result = method.handle(dev, session)
                if result is None:  # None indicates incompatibility
                    cls.log.info(
                        f'({tried_methods}/{len(methods)}) Method "{method.handler.__name__}" was not compatible'
                    )
                    used_methods[method.handler.__name__] = "NOT COMPAT"
                    continue

                for k in result:  # Check root keys for duplicates
                    if k in pulled_config:
                        cls.log.warning(
                            f"Key {k} is already present from a previous pull; overwriting..."
                        )

                # Report OK and update pulled config
                used_methods[method.handler.__name__] = "OK"
                pulled_config.update(result)
                cls.log.info(
                    f'({tried_methods}/{len(methods)}) Successfully used method "{method.handler.__name__}"'
                )

                sleep(1)
            except Exception as e:
                # Report error and mark not OK
                cls.log.exception(f"Exception caught: {e}")
                used_methods[method.handler.__name__] = "NOT OK"

        try:
            # Pull the index page to add extra data
            p.pull_index(dev, session, pulled_config)
        except Exception as e:
            cls.log.warning(f"Failed to pull data from dashboard: {e}")

        # Write relevant files

        dev.write_file(pulled_config, "web_cfg.json")  # Full web configuration
        dev.related.files.add("web_cfg.json")

        microconf = clone(pulled_config)
        if "syslog_report" in microconf:
            del microconf["syslog_report"]

        dev.write_file(microconf, "short_web_cfg.json")
        dev.related.files.add("short_web_cfg.json")

        dev.write_file(used_methods, "attempted_methods.json")
        dev.related.files.add("attempted_methods.json")

        webcfg_summarize(dev, pulled_config)

        cls.update_dev(dev)

        return True


# This seems to list the methods to be used to perform validation
SEL362X.ip_methods = [
    IPMethod(
        name="Perform a Web fingerprint (SEL-362x)",
        description=str(SEL362X._verify_http.__doc__).strip(),
        type="unicast_ip",
        identify_function=SEL362X._verify_http,
        default_port=443,
        protocol="https",
        reliability=8,
        transport="tcp",
    )
]
