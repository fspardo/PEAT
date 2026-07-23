"""
SEL-362X Security Gateway.

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

from time import sleep

from peat import DeviceData, DeviceModule, IPMethod, exit_handler

from .http import HTTP362X
from .method import AdvancedRange as AR
from .method import Method
from .pull import *


class SEL362X(DeviceModule):
    """
    SEL-3620 Security Gateway
    SEL-3622 Ethernet Security Gateway.
    """

    device_type = "Gateway"
    vendor_id = "SEL"
    vendor_name = "Schweitzer Engineering Laboratories"
    brand = "SEL"
    module_aliases = ["sel-3622", "sel-3620", "sel-362x", "3622", "3620", "362x"]
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

        # TODO: pull
        fid = session.get_fid()
        assert fid
        fid = fid.split("-")
        device = f"{fid[0]}-{fid[1]}"
        version = int(fid[2][1:])

        dev._cache["DEVICE"] = device
        dev._cache["VERSION"] = version

        methods = [  # List pull methods here ((dev: DeviceData, session) -> dict[str, Any])
            # Prepare for pull later
            Method(initialize_file_management_pull, 1, for_firmware=AR(None, 200)),
            # System
            Method(pull_usage_policy, 3),
            Method(pull_web_server_config, 3),
            # pull_file_management [moved to the end]
            Method(pull_physical_sensors, 3, ["sel-3622"]),
            # User
            Method(pull_users, 3),
            Method(pull_ldap_settings, 3),
            Method(pull_radius_settings, 3),
            Method(pull_local_groups, 3),
            # Network
            Method(pull_network_settings, 3),
            Method(pull_static_routes, 3),
            # TODO: pull NAT
            Method(pull_syslog_settings, 3),
            Method(pull_firewall_rules, 3),
            Method(pull_hosts, 3),
            Method(pull_snmp_settings, 3),
            # Serial Ports
            Method(pull_serial_port_settings, 3),
            Method(pull_serial_port_profiles, 3),
            Method(pull_port_mappings, 3),
            # Security
            Method(pull_certificates, 3),
            Method(pull_connections, 3),
            Method(pull_clients, 3),
            Method(pull_host_keys, 3),
            Method(pull_passwd_mgmt, 3),
            # Reports
            Method(pull_syslog_report, 3),
            Method(pull_diagnostics, 3, ["sel-3622"], 200),
            # File Management is last to allow for enough time to see an update to the configuration
            Method(pull_file_management, 1, for_firmware=AR(None, 200)),
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
                result = method.handle(dev, session)
                if result is None:
                    cls.log.info("Method was not compatible")
                    used_methods[method.handler.__name__] = "NOT COMPAT"
                    continue

                for k in result:
                    if k in pulled_config:
                        cls.log.warning(
                            f"Key {k} is already present from a previous pull; overwriting..."
                        )
                used_methods[method.handler.__name__] = "OK"
                pulled_config.update(result)
                cls.log.info("Successfully used method")
                sleep(1)
            except Exception as e:
                cls.log.exception(f"Exception caught: {e}")
                used_methods[method.handler.__name__] = "NOT OK"

        try:
            pull_index(dev, session, pulled_config)
        except Exception as e:
            cls.log.warning(f"Failed to pull data from dashboard: {e}")

        dev.write_file(pulled_config, "web_cfg.json")  # Full web configuration
        dev.write_file(used_methods, "attempted_methods.json")
        dev.related.files.add("web_cfg.json")
        cls.update_dev(dev)

        # TODO: populate device overview with data

        return True


# This seems to list the methods to be used to perform validation
SEL362X.ip_methods = [
    IPMethod(
        name="Perform a Web fingerprint (SEL-3622)",
        description=str(SEL362X._verify_http.__doc__).strip(),
        type="unicast_ip",
        identify_function=SEL362X._verify_http,
        default_port=443,
        protocol="https",
        reliability=5,  # TODO: Determine value
        transport="tcp",
    )
]
