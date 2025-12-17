from typing                                                                      import List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_github.surrogates.github.schemas.Enum__GitHub__Scope      import Enum__GitHub__Scope


class Schema__Surrogate__PAT(Type_Safe):                                        # PAT definition with associated scopes and state
    token           : str                                                       # The PAT string
    user_login      : str                                                       # Associated user login
    user_id         : int                                                       # Associated user ID
    scopes          : List[Enum__GitHub__Scope]                                 # Granted scopes
    is_valid        : bool                     = True                           # Is this a valid PAT
    is_expired      : bool                     = False                          # Has this PAT expired
    is_rate_limited : bool                     = False                          # Is this PAT rate limited

    def has_scope(self, scope: Enum__GitHub__Scope) -> bool:                    # Check if PAT has specific scope
        return scope in self.scopes

    def has_any_scope(self, scopes: List[Enum__GitHub__Scope]) -> bool:         # Check if PAT has any of the scopes
        return any(scope in self.scopes for scope in scopes)

    def can_read_repo_secrets(self) -> bool:                                    # Check if PAT can read repository secrets
        return self.has_any_scope([Enum__GitHub__Scope.REPO, Enum__GitHub__Scope.PUBLIC_REPO])

    def can_write_repo_secrets(self) -> bool:                                   # Check if PAT can write repository secrets
        return self.has_scope(Enum__GitHub__Scope.REPO)

    def can_admin_org(self) -> bool:                                            # Check if PAT can administer organization
        return self.has_scope(Enum__GitHub__Scope.ADMIN_ORG)

    def can_read_org(self) -> bool:                                             # Check if PAT can read organization
        return self.has_any_scope([Enum__GitHub__Scope.ADMIN_ORG  ,
                                   Enum__GitHub__Scope.WRITE_ORG  ,
                                   Enum__GitHub__Scope.READ_ORG   ])
