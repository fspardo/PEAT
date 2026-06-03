"""
SEL-3622 Security Gateway.

The docs call this a "small form-factor" version of the 3620,
but the differences seem to go deeper than calling it the
3620's dwarf brother.

Author: Francisco Santana <fsantan@sandia.gov>
"""

from peat import DeviceData, DeviceModule, IPMethod, exit_handler

from .http import HTTP3622 as SELHTTP


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

    session: SELHTTP | None = None

    @classmethod
    def get_session(cls, dev: DeviceData) -> SELHTTP | None:
        if cls.session:
            # TODO: determine how best to handle multiple devices
            return cls.session

        port = dev.options["https"]["port"]
        timeout = dev.options["https"]["timeout"]

        cls.log.debug(f"Verifying on port {port} with timeout {timeout}")

        session = SELHTTP(dev.ip, port, timeout)

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
            cls.session = session
            return session

    @classmethod
    def _verify_http(cls, dev: DeviceData) -> bool:
        """
        Validate that the device is an SEL-3622 via its HTTPS web interface
        """
        cls.log.info(f"SEL/3622: Verifying {dev.ip} via HTTPS")

        # TODO: perform validation

        session = cls.get_session(dev)
        if not session:
            cls.log.error("Failed to log in to the device!")
            return False

        if session.validate_fid():
            cls.log.info("Success! This device is an SEL-3622!")
        else:
            cls.log.error("Failure!")
            return False

        session.disconnect()

        return True

    @classmethod
    def _pull(cls, dev: DeviceData) -> bool:
        """
        Pull data from the SEL 3622
        """
        from .FileManagement import SystemSettings, SystemSettingsPoller

        cls.log.info(f"SEL/3622: Pulling information")

        session = cls.get_session(dev)
        if not session:
            cls.log.error("Failed to initialize session")
            return False

        # TODO: pull

        ssp = SystemSettingsPoller(session)
        if not ssp.queue():
            cls.log.error("Failed to queue system file generation")
            return False

        sys_settings = None

        # Query once every 30 seconds, for a total of 300s (5m).
        for i in range(0, 10):
            cls.log.debug(f"Query {i + 1} of 10...")
            from time import sleep

            sleep(30)
            sys_settings = ssp.query()
            if sys_settings is SystemSettings:
                cls.log.info("Pulled system configuration backup")
                break

            if not sys_settings:
                return False

        if not sys_settings is not SystemSettings:
            cls.log.info("Pulling system configuration backup...")
            sys_settings = ssp.query(force=True)
            if sys_settings is not SystemSettings:
                cls.log.error("Failed to pull the system configuration backup")
                return False

        cls.log.info("Pulled system configuration")

        # TODO: export configuration file

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
