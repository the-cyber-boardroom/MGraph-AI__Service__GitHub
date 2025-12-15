from typing                              import Optional
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__GitHub__Rate_Limit(Type_Safe):                                    # GitHub API rate limit information
    limit    : Optional[int] = None                                             # Rate limit ceiling
    remaining: Optional[int] = None                                             # Remaining requests in current window
    reset    : Optional[int] = None                                             # Unix timestamp when limit resets
    used     : Optional[int] = None                                             # Requests used in current window
