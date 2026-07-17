"""
Pull the device's web server configuration from /WebServer.sel.

Author: Nehal Mohamed Ameen <nmameen@sandia.gov>
"""

from typing import Any

from peat import DeviceData

from ..http import HTTP3622
from ..parse.WebServer import parse_web_server


def pull_web_server(dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
    """
    Pull from the /WebServer.sel endpoint.

    | Field                                   | Description                                      |
    |-----------------------------------------|--------------------------------------------------|
    | `web_server.server_time`                | Server time shown by the device web interface.   |
    | `web_server.port`                       | HTTPS web server port.                           |
    | `web_server.x509_certificate`           | Selected X.509 certificate name.                 |
    | `web_server.x509_certificates`          | Available X.509 certificate options.             |
    | `web_server.session_timeout`            | Global session timeout in minutes.               |
    | `web_server.available_network_addresses`| Network addresses available to add.              |
    | `web_server.addresses`                  | Configured web server management addresses.      |

    """
    response = session.get_endpoint("web_server")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception("Redirected")
    if response.status_code != 200:
        raise Exception("Non-200 status code")

    soup = session.gen_soup(response.text)

    return {"web_server": parse_web_server(soup)}
