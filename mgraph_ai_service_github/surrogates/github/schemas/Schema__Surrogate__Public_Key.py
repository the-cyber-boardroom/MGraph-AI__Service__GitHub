from typing                              import Dict, Any
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Surrogate__Public_Key(Type_Safe):                                 # Public key for secret encryption
    key_id     : str                                                            # Unique identifier
    key        : str                                                            # Base64-encoded public key
    created_at : str = '2024-01-01T00:00:00Z'                                   # ISO timestamp

    def to_github_response(self) -> Dict[str, Any]:                             # Convert to GitHub API response format
        return dict(key_id = self.key_id ,
                    key    = self.key    )
