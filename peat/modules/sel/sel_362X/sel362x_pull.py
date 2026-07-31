"""
Pull methods for the SEL 3622 and 3620

Authors:
    - Francisco Santana
    - Nehal Ameen
"""

from typing import Any, Literal

from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger

from peat import DeviceData

from .sel362x_file_backup import initialize_file_management_pull, pull_file_management
from .sel362x_http import HTTP362X
from .sel362x_parse import *
from .sel362x_parse_diagnostics import *

# ---------------------------------------------------------------------------- #
#                              AllowedClients.sel                              #
# ---------------------------------------------------------------------------- #


def pull_clients(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /AllowedClients.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("allowed_clients")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_clients(soup)

    return {"allowed_clients": result}


# ---------------------------------------------------------------------------- #
#                                Diagnostics.sel                               #
# ---------------------------------------------------------------------------- #


def pull_diagnostics(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /Diagnostics.sel
    """

    from . import AR

    response = session.get_endpoint("diagnostics")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    soup = session.gen_soup(response.text)

    if dev._cache["VERSION"] in AR(high=200):
        return {"diagnostics": parse_diagnostics_R200(soup)}
    else:
        return {"diagnostics": parse_diagnostics_R212(soup)}


# ---------------------------------------------------------------------------- #
#                                 Firewall.sel                                 #
# ---------------------------------------------------------------------------- #


def _correct_firewall_config_view(session: HTTP362X) -> str:
    response = session.get_endpoint("firewall")

    if not response:
        raise Exception("No response")
    elif response.status_code != 200:
        raise Exception("Non-200 status code")
    elif len(response.history) > 0:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    keys = [
        "dropPing",
        "dropTraceroute",
        "mustBeEncrypted",
        "allowAllEncrypted",
        "textOnly",
        "integrated",
        "t",
    ]

    def getinpt(soup: BeautifulSoup, k: str) -> str:
        v = soup.find("input", {"id": k})
        assert isinstance(v, Tag)
        v = v.get("value")
        assert isinstance(v, str)
        return v

    cfg = {k: getinpt(soup, k) for k in keys}

    for k in keys:
        if cfg[k] == "false":
            del cfg[k]

    cfg["FirewallRuleId"] = ""
    cfg["textOnly"] = "true"
    cfg["integrated"] = "true"
    cfg["submit"] = "Save"

    resp = session.post_endpoint("firewall", data=cfg)
    assert resp and resp.status_code == 200 and len(resp.history) == 0

    return resp.text


def pull_firewall_rules(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Corrects the Firewall view to integrate all rules into a singular list
    """
    return {
        "firewall": parse_firewall_rules(session.gen_soup(_correct_firewall_config_view(session)))
    }


# ---------------------------------------------------------------------------- #
#                                   Hosts.sel                                  #
# ---------------------------------------------------------------------------- #


def pull_hosts(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /Hosts.sel
    """

    response = session.get_endpoint("hosts")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"hosts": parse_hosts(session.gen_soup(response.text))}


# ---------------------------------------------------------------------------- #
#                                   index.sel                                  #
# ---------------------------------------------------------------------------- #


def pull_index(dev: DeviceData, session: HTTP362X, data: dict[str, Any]):
    """
    This works a bit differently. Some information is not available from the
    respective pages, while others are seemingly unique.

    This is to be run last.
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("dashboard")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    parse_index(soup, data)


# ---------------------------------------------------------------------------- #
#                                   IPsec.sel                                  #
# ---------------------------------------------------------------------------- #


def pull_ipsec_connections(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /IPsec.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ipsec_connections")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_ipsec_connections(soup)

    return {"ipsec": result}


# ---------------------------------------------------------------------------- #
#                                   LDAP.sel                                   #
# ---------------------------------------------------------------------------- #


def pull_ldap_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("ldap_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"ldap": parse_ldap_settings(session.gen_soup(response.text))}


# ---------------------------------------------------------------------------- #
#                                LocalGroups.sel                               #
# ---------------------------------------------------------------------------- #


def pull_local_groups(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("local_groups")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"local_groups": parse_local_groups(session.gen_soup(response.text))}


# ---------------------------------------------------------------------------- #
#                                    NAT.sel                                   #
# ---------------------------------------------------------------------------- #


def pull_nat_config(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the device's NAT config under /NAT.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("nat")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"NAT": parse_nat_config(session.gen_soup(response.text))}


# ---------------------------------------------------------------------------- #
#                              NetworkSettings.sel                             #
# ---------------------------------------------------------------------------- #


def pull_network_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /NetworkSettings.sel
    """

    response = session.get_endpoint("network_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    addresses, bridges = parse_network_addresses(soup)

    return {
        "network": {
            "global": parse_global_network_config(soup),
            "interfaces": parse_network_nics(soup),
            "addresses": addresses,
            "bridges": bridges,
        }
    }


# ---------------------------------------------------------------------------- #
#                            PasswordManagement.sel                            #
# ---------------------------------------------------------------------------- #


def pull_passwd_mgmt(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /PasswordManagement.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("password_management")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_passwd_mgmt(soup)

    return {"password_mgmt": result}


# ---------------------------------------------------------------------------- #
#                              PhysicalSensors.sel                             #
# ---------------------------------------------------------------------------- #


def pull_physical_sensors(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration of the physical sensors page
    """

    result = {}
    response = session.get_endpoint("physical_sensors")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception("Redirected")
    if response.status_code != 200:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    try:
        result["enabled"] = parse_sensors_enabled(soup)
    except Exception as e:
        logger.warning("Failed to get global status")
    try:
        result["input_contact"] = parse_sensor_input_contact(soup)
    except Exception as e:
        logger.warning("Failed to get input contact status")
    try:
        result["light"] = parse_sensor_light(soup)
    except Exception as e:
        logger.warning("Failed to get ligt sensor status")
    try:
        result["motion"] = parse_sensor_motion(soup)
    except Exception as e:
        logger.warning("Failed to get motion sensor status")

    return {"sensors": result}


# ---------------------------------------------------------------------------- #
#                                PortMapping.sel                               #
# ---------------------------------------------------------------------------- #


def pull_port_mappings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /PortMappings.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("port_mappings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Inspecting contents...")

    result = parse_port_mappings(soup)

    return {"port_mappings": result}


# ---------------------------------------------------------------------------- #
#                                  RADIUS.sel                                  #
# ---------------------------------------------------------------------------- #


def _pull_radius_dictionary(
    dev: DeviceData,
    session: HTTP362X,
    soup: BeautifulSoup,
) -> str | None:
    t = soup.find("input", {"name": "t"})
    if not isinstance(t, Tag):
        logger.error("Could not get token value")
        return None

    response = session.post_endpoint(
        "radius_settings",
        data={
            "t": t.get("value"),
            "download": "Download",
        },
    )

    if not response:
        logger.error("No response")
        return None

    if response.status_code != 200:
        logger.error("Could not pull file")
        return None

    if response.headers["Content-Type"] != "text/plain":
        logger.error("Incorrect content type")
        return None

    dev.write_file(response.text, "Dictionary.sel")
    dev.related.files.add("Dictionary.sel")
    return response.text


def pull_radius_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """
    logger.debug("Pulling page...")
    response = session.get_endpoint("radius_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_radius_settings(soup)

    logger.info("Pulling RADIUS dictionary...")
    try:
        d = _pull_radius_dictionary(dev, session, soup)
        if not d:
            logger.error("Failed to pull dictionary")
        result["dictionary"] = d
    except Exception as e:
        logger.error(f"Error pulling dictionary: {e}")

    return {"radius": result}


# ---------------------------------------------------------------------------- #
#                            SerialPortProfiles.sel                            #
# ---------------------------------------------------------------------------- #


def pull_serial_port_profiles(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SerialPortProfiles.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("serial_port_profiles")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_serial_port_profiles(soup)

    return {"serial_port_profiles": result}


# ---------------------------------------------------------------------------- #
#                            SerialPortSettings.sel                            #
# ---------------------------------------------------------------------------- #


def pull_serial_port_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SerialPortSettings.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("serial_port_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_serial_port_settings(soup)

    return {"serial_ports": result}


# ---------------------------------------------------------------------------- #
#                                   SNMP.sel                                   #
# ---------------------------------------------------------------------------- #


def _pull_snmp_mibs(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    logger.debug("Pulling SNMP MIBs...")

    response = session.get("SNMP_MIBs.sel")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception("Non-200 status")
    if len(response.history) > 0:
        raise Exception("Redirected")

    soup = session.gen_soup(response.text)
    t = soup.find("input", {"type": "hidden"})
    assert isinstance(t, Tag)
    t = t.get("value")
    assert t

    response = session.post(
        f"{session.url}/SNMP_MIBs.sel",
        data={"submit": "Download", "t": t},
    )

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception("Non-200 status")
    if len(response.history) > 0:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Writing MIBs ZIP file")
    dev.write_file(response.content, "MIBS.zip")

    return parse_mibs(dev, "MIBS.zip")


def pull_snmp_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /LDAP.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("snmp_settings")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")

    result = parse_snmp_settings(session.gen_soup(response.text))

    try:
        result.update(_pull_snmp_mibs(dev, session))
    except Exception as e:
        logger.error(f"Failed to pull SNMP MIBs files: {e}")

    return {"snmp": result}


# ---------------------------------------------------------------------------- #
#                               SSH_Host_Key.sel                               #
# ---------------------------------------------------------------------------- #


def pull_host_keys(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SSH_Host_Key.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("ssh_host_key")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_host_keys(soup)

    return {"host_keys": result}


# ---------------------------------------------------------------------------- #
#                               StaticRoutes.sel                               #
# ---------------------------------------------------------------------------- #


def pull_static_routes(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pulls data from the /StaticRoutes.sel endpoint
    """

    response = session.get_endpoint("static_routes")
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Status code {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    return {"static_routes": parse_static_routes(soup)}


# ---------------------------------------------------------------------------- #
#                                  Syslog.sel                                  #
# ---------------------------------------------------------------------------- #


def pull_syslog_settings(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /Syslog.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("syslog")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    logger.debug("Parsing page...")
    return {"syslog_settings": parse_syslog_settings(session.gen_soup(response.text))}


# ---------------------------------------------------------------------------- #
#                               SysLogReport.sel                               #
# ---------------------------------------------------------------------------- #


def pull_syslog_report(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /SysLogReport.sel

    Logs are sorted by ID, in ascending order
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("system_logs")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)
    t = soup.find("input", {"type": "hidden", "name": "t"})

    if not isinstance(t, Tag):
        raise Exception("Failed to find token")

    t = t.get("value")

    response = session.get(f"SysLogReport.sel?submit=download&t={t}")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    csv = response.text.splitlines()

    if csv[0] != "Id,Acked,Severity,Facility,Tag,Time,Message":
        raise Exception("Got incorrect data")

    logger.debug("Parsing page...")

    return {"syslog_report": parse_syslog_report(csv)}


# ---------------------------------------------------------------------------- #
#                                UsagePolicy.sel                               #
# ---------------------------------------------------------------------------- #


def pull_usage_policy(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull from the /UsagePolicy.sel endpoint
    """
    response = session.get_endpoint("usage_policy")

    if not response:
        raise Exception("No response")
    if len(response.history) > 0:
        raise Exception(f"Redirected to {response.history[-1].url}")
    if response.status_code != 200:
        raise Exception("Non-200 status code")

    soup = session.gen_soup(response.text)

    return {"usage_policy": parse_usage_policy(soup)}


# ---------------------------------------------------------------------------- #
#                                   Users.sel                                  #
# ---------------------------------------------------------------------------- #


def pull_users(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull registered users
    """
    result = {}

    # Get the page
    response = session.get_endpoint("accounts")
    # Check response
    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}")
    if response.history:
        raise Exception("Redirected")

    def _pull_user_info(dev: DeviceData, session: HTTP362X, row: Tag) -> dict[str, Any]:
        """
        Pull extended user info
        """
        # Get the URL from the Update button
        update = row.find("a", {"title": "Update"})
        if not isinstance(update, Tag):
            return {}
        # Get redirect path
        ref = update.get("href")

        # Get the username
        username = row.find("td", {"class": "ui_Username"})
        if not isinstance(username, Tag):
            return {}
        username = username.get_text(strip=True)

        # Get that page
        response = session.get(ref)
        if not response:
            raise Exception("No response")
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}")
        if response.history:
            raise Exception(f"Redirected to {response.history[-1].url}")

        return parse_user_info(dev, session.gen_soup(response.text))

    # Parse
    soup = session.gen_soup(response.text)

    # Extract table
    table = soup.find("table", {"id": "localUser"})
    if not isinstance(table, Tag):
        raise Exception("Could not find data table")

    # Parse rows
    rows = table.find_all("tr")[1:]
    for row in rows:
        result.update(_pull_user_info(dev, session, row))

    return {"users": result}


# ---------------------------------------------------------------------------- #
#                    WebServer.sel / ManagementInterface.sel                   #
# ---------------------------------------------------------------------------- #


def pull_web_server_config(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /WebServer.sel or /ManagementInterface.sel
    """

    logger.debug("Pulling page...")
    response = None
    if dev._cache["VERSION"] > 200:
        response = session.get_endpoint("management_interface")
    else:
        response = session.get_endpoint("web_server")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")
    result = parse_global_web_server_config(soup)
    result["listeners"] = parse_web_server_listeners(soup)

    return {"web_server": result}


# ---------------------------------------------------------------------------- #
#                                   X509.sel                                   #
# ---------------------------------------------------------------------------- #


def pull_certificates(dev: DeviceData, session: HTTP362X) -> dict[str, Any]:
    """
    Pull the configuration under /X509.sel
    """

    logger.debug("Pulling page...")
    response = session.get_endpoint("x509_certificates")

    if not response:
        raise Exception("No response")
    if response.status_code != 200:
        raise Exception(f"Got non-200 status: {response.status_code}")
    if response.history:
        raise Exception(f"Redirected to {response.history[-1].url}")

    soup = session.gen_soup(response.text)

    logger.debug("Parsing page...")

    result = parse_certificates_basic(soup)

    actions = soup.find_all("tr", {"class": ["even", "odd"]})
    actions = [
        (
            r.find("td", {"class": "x509_name"}),
            r.find("a", {"title": "View"}),
            r.find("a", {"title": "Export"}),
        )
        for r in actions
        if isinstance(r, Tag)
    ]
    hrefs = {
        n.get_text("", True): (v.get("href"), e.get("href"))
        for n, v, e in actions
        if isinstance(n, Tag) and isinstance(v, Tag) and isinstance(e, Tag)
    }

    for name in hrefs:
        logger.debug(f"Pulling additional configuration data for {name}...")
        response = session.get(hrefs[name][0])

        if not response:
            raise Exception("No response")
        if response.status_code != 200:
            raise Exception(f"Got non-200 status: {response.status_code}")
        if response.history:
            raise Exception(f"Redirected to {response.history[-1].url}")

        soup2 = session.gen_soup(response.text)

        # Replace data with more advanced parse output
        result[name] = parse_certificates_advanced(soup2)

        # Get certificate
        response = session.get(hrefs[name][1])

        if not response:
            raise Exception("No response")
        if response.status_code != 200:
            raise Exception(f"Got non-200 status: {response.status_code}")
        if response.history:
            raise Exception(f"Redirected to {response.history[-1].url}")

        dev.write_file(response.content, f"{name}.pem")
        dev.related.files.add(f"{name}.pem")

        result[name]["file"] = f"{name}.pem"

    return {"certificates": result}
