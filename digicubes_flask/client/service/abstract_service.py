"""
A base class for all service endpoint.
"""
from typing import Optional, Dict, Text

from digicubes_flask import exceptions as ex

__ALL__ = ["AbstractService"]


class AbstractService:
    """
    This is an abstract base class for all
    digicube services.
    """

    X_FILTER_FIELDS = "X-Filter-Fields"

    __slots__ = ["client"]

    def __init__(self, client) -> None:
        self.client = client

    @property
    def url(self) -> str:
        """The server url"""
        return self.client.url

    @property
    def cache(self):
        return self.client.cache

    @property
    def requests(self):
        """
        Returns the requests object.
        """
        return self.client.requests

    def create_default_header(self, token) -> Dict[Text, Text]:
        """
        Creates the default header for a standard
        call. Sets the bearer token as well as the
        accept header.
        """
        auth_value = f"Bearer {token}"
        return {"Authorization": auth_value, "Accept": "application/json"}

    def url_for(self, route: str, **kwargs) -> str:
        # pylint: disable=C0111
        return self.client.url_for(route, **kwargs)

    def check_response_status(self, response, expected_status: Optional[int] = None):
        """
        A default handler for the most common exception.
        """
        if response.status_code == 401:
            raise ex.TokenExpired(response.text)

        if response.status_code == 403:
            raise ex.InsufficientRights(response.text)

        if response.status_code == 404:
            raise ex.DoesNotExist(response.text)

        if response.status_code == 409:
            raise ex.ConstraintViolation(response.text)

        if response.status_code == 500:
            raise ex.ServerError(response.text)

        if expected_status and response.status_code != expected_status:
            raise ex.ServerError(
                f"Unexpected status. Expected {expected_status} but got {response.status_code} - {response.text}"
            )
