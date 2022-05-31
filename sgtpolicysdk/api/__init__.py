"""Cisco DNA Center API wrappers for sgt and policy APIs.
Copyright (c) 2021-2022 Cisco Systems.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from past.types import basestring

from ..config import (
    DEFAULT_DEBUG,
    DEFAULT_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_SINGLE_REQUEST_TIMEOUT,
    DEFAULT_WAIT_ON_RATE_LIMIT,
    DEFAULT_VERIFY,
)

import sgtpolicysdk.environment as dnacsgtpolicy_environment
from sgtpolicysdk.utils import check_type
from sgtpolicysdk.client_manager import DnacClientManager
#Internal Modules
from .v2_3_3_3.task import Task as Task_v2_3_3_3
from .v2_3_3_3.securitygroups import SecurityGroups as SecurityGroups_v2_3_3_3
from .v2_3_3_3.accesscontract import AccessContracts as AccessContracts_v2_3_3_3
from .v2_3_3_3.sgtpolicy import SGTPolicy as SGTPolicy_v2_3_3_3


class DNACenterSGTPolicyAPI(object):
    """Cisco DNA Center API wrapper.
    Creates a 'session' for all API calls through a created DNACenterAPI
    object.  The 'session' handles authentication, provides the needed headers,
    and checks all responses for error conditions.
    DNASGTPolicyCenterAPI wraps all of the individual DNA SGTPolicy Center APIs and represents
    them in a simple hierarchical structure.
    """

    def __init__(self,
                 server=None, 
                 username=None,
                 password=None,
                 base_url=None,
                 single_request_timeout=None,
                 wait_on_rate_limit=None,
                 verify=None,
                 version='2.3.3.3',
                 api_version="v1",
                 debug=None,
                 connect=True):
        """Create a new DNASGTPolicyCenterAPI object.
        An access token is required to interact with the DNA Center APIs.
        This package supports two methods for you to generate the
        authorization token:
          1. Provide a encoded_auth value (username:password encoded in
          base 64). *This has priority over the following method*
          2. Provide username and password values.
        This package supports two methods for you to set those values:
          1. Provide the parameter. That is the encoded_auth or
          username and password parameters.
          2. If an argument is not supplied, the package checks for
          its environment variable counterpart. That is the
          DNA_CENTER_ENCODED_AUTH, DNA_CENTER_USERNAME,
          DNA_CENTER_PASSWORD.
        When not given enough parameters an AccessTokenError is raised.
        Args:
            base_url(basestring): The base URL to be prefixed to the
                individual API endpoint suffixes.
                Defaults to the DNA_CENTER_BASE_URL environment variable or
                sgtpolicysdk.config.DEFAULT_BASE_URL
                if the environment variable is not set.
            username(basestring): HTTP Basic Auth username.
            password(basestring): HTTP Basic Auth password.
            encoded_auth(basestring): HTTP Basic Auth base64 encoded string.
            single_request_timeout(int): Timeout (in seconds) for RESTful HTTP
                requests. Defaults to the DNA_CENTER_SINGLE_REQUEST_TIMEOUT
                environment variable or
                sgtpolicysdk.config.DEFAULT_SINGLE_REQUEST_TIMEOUT
                if the environment variable is not set.
            wait_on_rate_limit(bool): Enables or disables automatic rate-limit
                handling. Defaults to the DNA_CENTER_WAIT_ON_RATE_LIMIT
                environment variable or
                sgtpolicysdk.config.DEFAULT_WAIT_ON_RATE_LIMIT
                if the environment variable is not set.
            verify(bool,basestring): Controls whether we verify the server's
                TLS certificate, or a string, in which case it must be a path
                to a CA bundle to use. Defaults to the DNA_CENTER_VERIFY
                (or DNA_CENTER_VERIFY_STRING) environment variable or
                sgtpolicysdk.config.DEFAULT_VERIFY if the environment
                variables are not set.
            version(basestring): Controls which version of DNA_CENTER to use.
                Defaults to the DNA_CENTER_VERSION environment variable or
                sgtpolicysdk.config.DEFAULT_VERSION
                if the environment variable is not set.
            debug(bool,basestring): Controls whether to log information about
                DNA Center APIs' request and response process.
                Defaults to the DNA_CENTER_DEBUG environment variable or False
                if the environment variable is not set.

        Returns:
            DNACenterAPI: A new DNACenterAPI object.

        """
        username = username or dnacsgtpolicy_environment.get_env_username()
        password = password or dnacsgtpolicy_environment.get_env_password()
        base_url = base_url or dnacsgtpolicy_environment.get_env_base_url() or DEFAULT_BASE_URL

        if single_request_timeout is None:
            single_request_timeout = dnacsgtpolicy_environment.get_env_single_request_timeout() or DEFAULT_SINGLE_REQUEST_TIMEOUT

        if wait_on_rate_limit is None:
            wait_on_rate_limit = dnacsgtpolicy_environment.get_env_wait_on_rate_limit() or DEFAULT_WAIT_ON_RATE_LIMIT

        if verify is None:
            verify = dnacsgtpolicy_environment.get_env_verify() or DEFAULT_VERIFY

        version = version or dnacsgtpolicy_environment.get_env_version() or DEFAULT_VERSION

        if debug is None:
            debug = dnacsgtpolicy_environment.get_env_debug() or DEFAULT_DEBUG

        check_type(base_url, basestring)
        check_type(single_request_timeout, int)
        check_type(wait_on_rate_limit, bool)
        check_type(debug, (bool, basestring), may_be_none=True)
        check_type(username, basestring, may_be_none=True)
        check_type(password, basestring, may_be_none=True)
        check_type(verify, (bool, basestring), may_be_none=False)

        if isinstance(debug, str):
            debug = 'true' in debug.lower()

        # Create the API session
        # All of the API calls associated with a DNASGTpolicyCenterAPI object will
        # leverage a single RESTful 'session' connecting to the DNA Center
        # cloud.
        
        self._session = DnacClientManager(server=server,username=username, password=password,base_url=base_url)

        # API wrappers
        if version == '2.3.3.3':
            self.task = \
                Task_v2_3_3_3(self._session)
            self.securitygroups = \
                SecurityGroups_v2_3_3_3(self)
            self.accesscontracts = \
                AccessContracts_v2_3_3_3(self)
            self.sgtpolicy = \
                SGTPolicy_v2_3_3_3(self)
    @property
    def session(self):
        """The DNA Center API session."""
        return self._session

    @property
    def base_url(self):
        """The base URL prefixed to the individual API endpoint suffixes."""
        return self._session.base_url

    @property
    def single_request_timeout(self):
        """Timeout (in seconds) for an single HTTP request."""
        return self._session.single_request_timeout

    @property
    def wait_on_rate_limit(self):
        """Automatic rate-limit handling enabled / disabled."""
        return self._session.wait_on_rate_limit

    @property
    def verify(self):
        """The verify (TLS Certificate) for the API endpoints."""
        return self._session._verify

    @property
    def version(self):
        """The API version of DNA Center."""
        return self._session._version

    @verify.setter
    def verify(self, value):
        """The verify (TLS Certificate) for the API endpoints."""
        self.authentication.verify = value
        self._session.verify = value

    @base_url.setter
    def base_url(self, value):
        """The base URL for the API endpoints."""
        self._session.base_url = value

    @single_request_timeout.setter
    def single_request_timeout(self, value):
        """The timeout (seconds) for a single HTTP REST API request."""
        self.authentication.single_request_timeout = value
        self._session.single_request_timeout = value

    @wait_on_rate_limit.setter
    def wait_on_rate_limit(self, value):
        """Enable or disable automatic rate-limit handling."""
        self._session.wait_on_rate_limit = value

        
