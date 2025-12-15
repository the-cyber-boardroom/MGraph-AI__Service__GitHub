from enum import Enum


class Enum__HTTP__Status(Enum):                                                 # HTTP status codes for API responses
    OK_200          = 200
    CREATED_201     = 201
    NO_CONTENT_204  = 204
    BAD_REQUEST_400 = 400
    UNAUTHORIZED_401= 401
    FORBIDDEN_403   = 403
    NOT_FOUND_404   = 404
    RATE_LIMITED_429= 429
    SERVER_ERROR_500= 500
