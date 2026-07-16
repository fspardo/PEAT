"""
SEL HTTP module specialized for the SEL-3622

Authors:
    - Francisco Santana <fsantan@sandia.gov>
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag

from ..sel_http import SELHTTP, Response
from .endpoints import AVAILABLE_ENDPOINTS, ENDPOINTS


class HTTP3622(SELHTTP):
    """
    Class specialization of `SELHTTP` for the SEL-3622.
    """

    def get(self, *args, **kwargs) -> Response | None:
        if "use_cache" not in kwargs:
            return super().get(*args, use_cache=False, **kwargs)
        else:
            return super().get(*args, **kwargs)

    def get_endpoint(self, page: AVAILABLE_ENDPOINTS, *args, **kwargs) -> Response | None:
        """
        Simplification of the "get" function which takes the name of the endpoint
        """
        return self.get(ENDPOINTS[page], *args, **kwargs)

    def post_endpoint(self, page: AVAILABLE_ENDPOINTS, *args, **kwargs) -> Response | None:
        """
        Simplification of the "post" function which takes the name of the endpoint
        """
        return self.post(self.endpoint(page), *args, **kwargs)

    def endpoint(self, endpoint: AVAILABLE_ENDPOINTS) -> str:
        """
        Generate an endpoint URL (necessary in post for some reason)
        """

        if endpoint not in ENDPOINTS:
            raise IndexError(f"Endpoint {endpoint} not available")
        else:
            return urljoin(self.url, ENDPOINTS[endpoint])

    def is_logged_in(self) -> bool:
        """
        Check if the session is still logged in
        """

        result = self.get("/index.sel", allow_redirects=False)

        return not result or (
            result.ok and not (result.is_redirect or result.is_permanent_redirect)
        )

    def needs_selssid(self, soup: BeautifulSoup) -> bool:
        """Checks if the SELSSID token is required to log in"""
        return isinstance(soup.find("input", {"name": "SELSESSID", "type": "hidden"}), Tag)

    def login(self, user: str = "admin", passwd: str = "Admin123!") -> bool:
        """
        Attempt to log in using the SEL-3622 Gateway's web interface.

        The SEL-3622 differs from the SEL-3620 quite a bit. Must be the Ozempic.
        """

        self.protocol = "https"
        # We only need login data and the Submit button
        login_data = {
            "Username": user,
            "Password": passwd,
            "submit": "Submit",
        }

        # Voodoo magicks be here
        # Gets a session cookie
        resp = self.get(ENDPOINTS["login"], "https")
        if not resp:
            self.log.error("Could not get login page")
            return False

        ssid = self.session.cookies["SELSESSID"]
        if not ssid:
            self.log.error("Did not get a session ID")
            return False

        self.session_id = ssid

        if self.needs_selssid(self.gen_soup(resp.text)):
            login_data["SELSESSID"] = ssid

        # NOTE: attempting to log in with a short timeout will fail.
        # At least 10 seconds will suffice.
        resp = self.post(self.endpoint("login"), data=login_data, timeout=max(self.timeout, 10))

        # Null response means no host
        if not resp:
            self.log.warning("Received no response.")
            return False

        # Non-200 response indicates an error
        if resp.status_code != 200:
            self.log.error(f"Login failed: received non-200 response ({resp.status_code}).")
            return False

        # Log-in failure
        # This more specific query will yield fewer false positives
        if "<!-- # ERROR MESSAGES # -->" in resp.text:
            self.log.error("Failed to log in")

        self.gateway_logged_in = True
        self.gateway = "SEL-3622"

        return True

    def get_global_token_value(self) -> str:
        response = self.get_endpoint("device_reset")
        if not response or not response.status_code == 200 or len(response.history) > 0:
            raise Exception("Could not get token")

        soup = self.gen_soup(response.text)
        t = soup.find("input", {"type": "hidden", "name": "t"})
        assert isinstance(t, Tag)

        return t.get_text(strip=True)

    def get_fid(self) -> str | None:
        """
        Get the FID of the device. Typically, this contains the device model.
        """

        assert self.gateway_logged_in
        assert self.gateway in ["SEL-3622", "SEL-3620"]

        idx = self.get(ENDPOINTS["dashboard"], use_cache=False)
        if not idx:
            self.log.error(f"Could not get {ENDPOINTS['dashboard']}")
            return None

        # We can perform an explicit check for the device's FID.
        idx_soup = self.gen_soup(idx.text)

        fid = idx_soup.find("td", {"id": "fid"})
        if not isinstance(fid, Tag):
            self.log.error("Could not get fid field")
            return None
        txt = fid.get_text()

        self.log.debug(f"FID: {txt}")

        return txt

    def validate_fid(self) -> bool:
        """
        Validate that the SEL is a supported SEL-3620 or SEL-3622 device
        """
        VALID_FID_SUBSTRINGS = ["SEL-3622", "SEL-3620"]

        fid_txt = self.get_fid()

        if not fid_txt or not any([x in fid_txt for x in VALID_FID_SUBSTRINGS]):
            self.log.error("This device is not an SEL-3620 or SEL-3622")
            return False

        return True

    def logout(self):
        """
        Log out of an SEL-3622 gateway
        """
        if self.gateway_logged_in and self.gateway not in ["SEL-3622", "SEL-3620"]:
            self.get(ENDPOINTS["logout"], use_cache=False)
            self.gateway_logged_in = False
            del self.gateway

    def disconnect(self) -> None:
        if self.gateway_logged_in and self.gateway not in ["SEL-3622", "SEL-3620"]:
            self.logout()
        return super().disconnect()


__all__ = ["HTTP3622"]
