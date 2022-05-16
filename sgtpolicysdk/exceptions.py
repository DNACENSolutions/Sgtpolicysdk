import logging
logger = logging.getLogger("Exception")

class DnacException(Exception):
    """ Base exception class in sgtpolicysdk takes an error message to get initialized

    It makes a log entry of level exception using the error message used while calling
    DnacException. The log entry has a tag of [DnacException], for the purpose of
    easy filtering.

    DnacException can be directly raised as an exception as well.

    Usage:
        raise DnacException("error_message")
    """

    # Class variable to keep count of the number of times the DnacException is raised in
    # the life of a test case.
    __COUNTER = 0

    __EXTRA_ACTIONS = set()

    def __init__(self, error_message):
        """ Initializes the test exception instance. """

        super(DnacException, self).__init__()
        self.__class__.__COUNTER += 1
        logger.log.error("[{0}] {1}".format(self.__class__.__name__, error_message))
        self.error_message = error_message
        for action in self.__class__.__EXTRA_ACTIONS:
            action()

    def __str__(self):
        return self.error_message

    @classmethod
    def set_extra_action(cls, method):
        """ Set what actions to take when DnacException object being created.

        Args:
            method (function): method to call when object init.
        """

        cls.__EXTRA_ACTIONS.add(method)

class ApiClientException(DnacException):
    """ Exception class for API specific scenarios"""

    def __init__(self, message=None):
        super(ApiClientException, self).__init__(message)

    @staticmethod
    def raise_exception(message=None, code=None):
        """ Raises exception based on the error code

        Args:
            message(str): response
            code (int): status code of the response

        Raises:
            InvalidContentException: when response error code is 400
            UnauthorizedException: when response error code is 401
            ApiNotFoundException: when response error code is 404
        """

        if code == 400:
            #TODO (hikoppu): Add more expections if any, which raise 404
            raise InvalidContentException(message)
        elif code == 401:
            raise UnauthorizedException(message)
        elif code == 404:
            #TODO (hikoppu): Add more expections if any, which raise 404
            raise ApiNotFoundException(message)

class ConnectionException(ApiClientException):
    """ Exception class for Connection specific scenarios. """

    def __init__(self, message=None):

        super(ConnectionException, self).__init__(
            message if message else "Connection to the server failed.")

class InvalidContentException(ApiClientException):
    """ Exception class for API with invalid content specific scenarios. """

    def __init__(self, message=None):

        super(InvalidContentException, self).__init__(
            message if message else "Invalid content in request. ")

class UnauthorizedException(ApiClientException):
    """ Exception class for API with no authorization specific scenarios. """

    def __init__(self, message=None):

        super(UnauthorizedException, self).__init__(
            message if message else "Unable to autheticate.")

class ApiNotFoundException(ApiClientException):
    """ Exception class for unrecognized API specific scenarios. """

    def __init__(self, message=None):

        super(ApiNotFoundException, self).__init__(
            message if message else "Unrecognized API called.")
