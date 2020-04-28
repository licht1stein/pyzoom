class BaseError(Exception):
    pass


class InvalidData(Exception):
    pass


class APIError(BaseError):
    pass


class NotFound(APIError):
    pass


class BadRequest(APIError):
    pass


class NotAuthorized(APIError):
    pass


class NotAllowed(APIError):
    pass


class Conflict(APIError):
    pass


HTTP_ERRORS_MAP = {
    400: BadRequest,
    401: NotAuthorized,
    404: NotFound,
    405: NotAllowed,
    409: Conflict,
}
