from typing                              import Dict, Any
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Surrogate__Rate_Limit(Type_Safe):                                 # GitHub rate limit tracking for surrogate
    limit     : int = 5000                                                      # Rate limit ceiling
    remaining : int = 4999                                                      # Remaining requests in current window
    reset     : int = 0                                                         # Unix timestamp when limit resets
    used      : int = 1                                                         # Requests used in current window

    def to_github_response(self) -> Dict[str, Any]:                             # Convert to GitHub API response format
        return dict(rate = dict(limit     = self.limit     ,
                                remaining = self.remaining ,
                                reset     = self.reset     ,
                                used      = self.used      ))

    def decrement(self) -> 'Schema__Surrogate__Rate_Limit':                     # Record a request
        self.remaining = max(0, self.remaining - 1)
        self.used     += 1
        return self
