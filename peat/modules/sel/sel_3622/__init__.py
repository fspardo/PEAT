"""
SEL-3622 Security Gateway.

The docs call this a "small form-factor" version of the 3620,
but the differences seem to go deeper than calling it the
3620's dwarf brother.

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

from peat import DeviceData, DeviceModule, IPMethod, exit_handler

from .http import HTTP3622
from .pull import *


class SEL3622(DeviceModule):
    """
    SEL-3622 Ethernet Security Gateway.

    AKA the SEL-3620 Slim.
    """

    device_type = "Gateway"
    vendor_id = "SEL"
    vendor_name = "Schweitzer Engineering Laboratories"
    brand = "SEL"
    module_aliases = ["sel-3622", "3622", "sel-3620-slim", "3620-slim"]
    default_options = {"web": {"user": "admin", "pass": "IAmAdmin!1", "users": []}}

    @classmethod
    def get_session(cls, dev: DeviceData) -> HTTP3622 | None:
        """
        Get the session associated with the device
        """
        if "web_session" in dev._cache:
            session = dev._cache["web_session"]
            assert isinstance(session, HTTP3622)
            if session.is_logged_in():
                return session

        port = dev.options["https"]["port"]
        timeout = dev.options["https"]["timeout"]

        cls.log.debug(f"Verifying on port {port} with timeout {timeout}")

        session = HTTP3622(dev.ip, port, timeout)

        user = None
        passwd = None

        if dev._cache.get("verified_web_user") and dev._cache.get("verified_web_pass"):
            user = dev._cache["verified_web_user"]
            passwd = dev._cache["verified_web_pass"]
        else:
            if dev.options["web"]["user"]:
                user = dev.options["web"]["user"]
                passwd = dev.options["web"]["pass"]

                assert isinstance(user, str)
                assert isinstance(passwd, str)
            else:
                user = cls.default_options["web"]["user"]
                passwd = cls.default_options["web"]["pass"]

        cls.log.debug(f"Attempting log-in as {user}/{passwd}")
        if not session.login(user, passwd):
            cls.log.error("Failed to log in to the device!")
            return None
        else:
            dev._cache["web_session"] = session
            dev._cache["global_token"] = session.get_global_token_value()
            return session

    @classmethod
    def _verify_http(cls, dev: DeviceData) -> bool:
        """
        Validate that the device is an SEL-3622 via its HTTPS web interface
        """
        cls.log.info(f"SEL/3622: Verifying {dev.ip} via HTTPS")

        session = cls.get_session(dev)
        if not session:
            cls.log.error("Failed to log in to the device!")
            return False

        if session.validate_fid():
            cls.log.info("Success! This device is an SEL-3622!")
        else:
            cls.log.error("Failure!")
            return False

        return True

    @classmethod
    def _pull(cls, dev: DeviceData) -> bool:
        """
        Pull data from the SEL 3622
        """

        cls.log.info(f"SEL/3622: Pulling information")

        session = cls.get_session(dev)
        port = dev.options["https"]["port"]
        if not session:
            cls.log.error("Failed to initialize session")
            return False

        # TODO: pull

        methods = [  # List pull methods here ((dev: DeviceData, session) -> dict[str, Any])
            # Prepare for pull later
            initialize_file_management_pull,
            # System
            pull_usage_policy,
            # pull_file_management [moved to the end]
            pull_physical_sensors,
            # User
            pull_users,
            pull_ldap_settings,
            pull_radius_settings,
            pull_local_groups,
            # Network
            pull_network_settings,
            pull_static_routes,
            pull_syslog_settings,
            # Serial Ports
            # Security
            # Reports
            # File Management is last to allow for enough time to see an update to the configuration
            pull_file_management,
        ]
        pulled_config = {}

        tried_methods = 0

        for method in methods:
            tried_methods += 1
            cls.log.info(
                f'({tried_methods}/{len(methods)}) Attempting method "{method.__name__} for {dev.ip}:{port}"'
            )

            try:
                result = method(dev, session)
                pulled_config.update(result)
                cls.log.info("Successfully used method")
            except Exception as e:
                cls.log.exception(f"Exception caught: {e}")

        dev.write_file(pulled_config, "web_cfg.json")
        dev.related.files.add("web_cfg.json")
        cls.update_dev(dev)

        return True


# This seems to list the methods to be used to perform validation
SEL3622.ip_methods = [
    IPMethod(
        name="Perform a Web fingerprint (SEL-3622)",
        description=str(SEL3622._verify_http.__doc__).strip(),
        type="unicast_ip",
        identify_function=SEL3622._verify_http,
        default_port=443,
        protocol="https",
        reliability=5,  # TODO: Determine value
        transport="tcp",
    )
]

__all__ = ["SEL3622"]
