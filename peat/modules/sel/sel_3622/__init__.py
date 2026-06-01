"""
SEL-3622 Security Gateway.

Authors

- Francisco Santana
"""

from peat import DeviceData, DeviceModule, IPMethod, exit_handler

from .sel_http import SELHTTP


class SEL3622(DeviceModule):
    """
    SEL-3622 Ethernet Security Gateway.

    AKA the SEL-3620 Slim.
    """

    device_type = "Gateway"
    vendor_id = "SEL"
    vendor_name = "Schweitzer Engineering Laboratories"
    brand = "SEL"
    module_aliases = [ 'sel-3622', '3622', 'sel-3620-slim', '3620-slim' ]
    default_options = {
        'web': {
            'user': 'admin',
            'pass': 'IAmAdmin',
            'users': []
        }
    }

    def _verify_http(self, dev: DeviceData) -> bool:
        """
        Validate that the device is an SEL-3622 via its HTTPS web interface
        """
        self.log.info(f"SEL/3622: Verifying {dev.ip} via HTTP")

        # TODO: perform validation

        return False

    # Override?
    def _pull(self, dev: DeviceData) -> bool:
        self.log.info(f"SEL/3622: Pulling information")

        # TODO: pull

        return False

# This seems to list the methods to be used to perform validation
SEL3622.ip_methods = [
    IPMethod(
        name="sel_3622_web_fingerprint",
        description=str(SEL3622._verify_http.__doc__).strip(),
        type="unicast_ip",
        identify_function=SEL3622._verify_http,
        default_port=443,
        protocol="https",
        reliability=5, # TODO: Determine value
        transport="tcp",
    )
]

__all__ = ["SEL3622"]