from enum import Enum


class Enum__Error__Type(Enum):                                                  # Error type classification for API responses
    NONE               = "none"
    INVALID_INPUT      = "invalid_input"
    MISSING_FIELD      = "missing_field"
    DECRYPTION_FAILED  = "decryption_failed"
    INVALID_PAT        = "invalid_pat"
    PAT_EXPIRED        = "pat_expired"
    INSUFFICIENT_SCOPES= "insufficient_scopes"
    NOT_FOUND          = "not_found"
    RATE_LIMITED       = "rate_limited"
    FORBIDDEN          = "forbidden"
    GITHUB_API_ERROR   = "github_api_error"
    SERVER_ERROR       = "server_error"
