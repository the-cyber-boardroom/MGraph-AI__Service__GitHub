from typing                              import Optional, Dict, Any
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Surrogate__Secret(Type_Safe):                                     # GitHub secret representation for surrogate
    name            : str                                                       # Secret name
    created_at      : str                      = '2024-01-01T00:00:00Z'         # ISO timestamp when created
    updated_at      : str                      = '2024-01-01T00:00:00Z'         # ISO timestamp when last updated
    encrypted_value : Optional[str]            = None                           # Base64-encoded encrypted value (stored for validation)
    key_id          : Optional[str]            = None                           # Key ID used for encryption

    def to_github_response(self) -> Dict[str, Any]:                             # Convert to GitHub API response format (metadata only)
        return dict(name       = self.name       ,
                    created_at = self.created_at ,
                    updated_at = self.updated_at )


class Schema__Surrogate__Org__Secret(Type_Safe):                                # GitHub organization secret with visibility
    name                      : str                                             # Secret name
    created_at                : str            = '2024-01-01T00:00:00Z'         # ISO timestamp when created
    updated_at                : str            = '2024-01-01T00:00:00Z'         # ISO timestamp when last updated
    visibility                : str            = 'private'                      # 'all', 'private', or 'selected'
    selected_repositories_url : Optional[str]  = None                           # URL for selected repos
    encrypted_value           : Optional[str]  = None                           # Base64-encoded encrypted value
    key_id                    : Optional[str]  = None                           # Key ID used for encryption

    def to_github_response(self) -> Dict[str, Any]:                             # Convert to GitHub API response format
        return dict(name                      = self.name                      ,
                    created_at                = self.created_at                ,
                    updated_at                = self.updated_at                ,
                    visibility                = self.visibility                ,
                    selected_repositories_url = self.selected_repositories_url )
