from typing                                                                      import Dict, Optional, List
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_github.surrogates.github.schemas.Enum__GitHub__Scope      import Enum__GitHub__Scope
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__PAT   import Schema__Surrogate__PAT
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__User  import Schema__Surrogate__User


class GitHub__API__Surrogate__PATs(Type_Safe):                                  # Pre-defined PATs for testing various permission scenarios
    
    # PAT Constants (40 chars like real GitHub PATs: ghp_ + 36 chars)
    PAT__ADMIN          : str = 'ghp_surrogate_admin_'         + 'A' * 21       # Full access
    PAT__REPO_WRITE     : str = 'ghp_surrogate_repo_write_'    + 'B' * 17       # Repo secrets write
    PAT__REPO_READ      : str = 'ghp_surrogate_repo_read_'     + 'C' * 18       # Repo secrets read-only
    PAT__ORG_ADMIN      : str = 'ghp_surrogate_org_admin_'     + 'D' * 17       # Org-level access
    PAT__ENV_ONLY       : str = 'ghp_surrogate_env_only_'      + 'E' * 18       # Environment secrets only
    PAT__EXPIRED        : str = 'ghp_surrogate_expired_'       + 'F' * 19       # Returns 401
    PAT__RATE_LIMITED   : str = 'ghp_surrogate_rate_limited_'  + 'G' * 14       # Returns 429
    PAT__NO_SCOPES      : str = 'ghp_surrogate_no_scopes_'     + 'H' * 17       # Returns 403 on operations
    PAT__INVALID        : str = 'ghp_surrogate_invalid_'       + 'I' * 19       # Returns 401
    
    # PAT definitions with scopes
    _pats  : Dict[str, Schema__Surrogate__PAT]
    _users : Dict[str, Schema__Surrogate__User]                                 # Users indexed by PAT
    
    def setup(self) -> 'GitHub__API__Surrogate__PATs':                          # Initialize PAT definitions
        self._pats  = {}
        self._users = {}
        self._setup_pats()
        return self
    
    def _setup_pats(self):                                                      # Create all PAT definitions
        # Admin PAT - full access
        self._add_pat(token       = self.PAT__ADMIN                                    ,
                      user_login  = 'surrogate-admin'                                  ,
                      user_id     = 1000001                                            ,
                      scopes      = [Enum__GitHub__Scope.REPO      ,
                                     Enum__GitHub__Scope.ADMIN_ORG ,
                                     Enum__GitHub__Scope.WORKFLOW  ]                   ,
                      user_name   = 'Surrogate Admin User'                             ,
                      user_email  = 'admin@surrogate.local'                            )
        
        # Repo write PAT
        self._add_pat(token       = self.PAT__REPO_WRITE                               ,
                      user_login  = 'surrogate-repo-write'                             ,
                      user_id     = 1000002                                            ,
                      scopes      = [Enum__GitHub__Scope.REPO]                         ,
                      user_name   = 'Surrogate Repo Write User'                        ,
                      user_email  = 'repo-write@surrogate.local'                       )
        
        # Repo read PAT
        self._add_pat(token       = self.PAT__REPO_READ                                ,
                      user_login  = 'surrogate-repo-read'                              ,
                      user_id     = 1000003                                            ,
                      scopes      = [Enum__GitHub__Scope.PUBLIC_REPO]                  ,
                      user_name   = 'Surrogate Repo Read User'                         ,
                      user_email  = 'repo-read@surrogate.local'                        )
        
        # Org admin PAT
        self._add_pat(token       = self.PAT__ORG_ADMIN                                ,
                      user_login  = 'surrogate-org-admin'                              ,
                      user_id     = 1000004                                            ,
                      scopes      = [Enum__GitHub__Scope.REPO      ,
                                     Enum__GitHub__Scope.ADMIN_ORG ]                   ,
                      user_name   = 'Surrogate Org Admin User'                         ,
                      user_email  = 'org-admin@surrogate.local'                        )
        
        # Env only PAT - can access environment secrets via workflow scope
        self._add_pat(token       = self.PAT__ENV_ONLY                                 ,
                      user_login  = 'surrogate-env-only'                               ,
                      user_id     = 1000005                                            ,
                      scopes      = [Enum__GitHub__Scope.WORKFLOW]                     ,
                      user_name   = 'Surrogate Env Only User'                          ,
                      user_email  = 'env-only@surrogate.local'                         )
        
        # Expired PAT
        self._add_pat(token       = self.PAT__EXPIRED                                  ,
                      user_login  = 'surrogate-expired'                                ,
                      user_id     = 1000006                                            ,
                      scopes      = []                                                 ,
                      is_expired  = True                                               ,
                      user_name   = 'Surrogate Expired User'                           ,
                      user_email  = 'expired@surrogate.local'                          )
        
        # Rate limited PAT
        self._add_pat(token           = self.PAT__RATE_LIMITED                         ,
                      user_login      = 'surrogate-rate-limited'                       ,
                      user_id         = 1000007                                        ,
                      scopes          = [Enum__GitHub__Scope.REPO]                     ,
                      is_rate_limited = True                                           ,
                      user_name       = 'Surrogate Rate Limited User'                  ,
                      user_email      = 'rate-limited@surrogate.local'                 )
        
        # No scopes PAT - valid but no permissions
        self._add_pat(token       = self.PAT__NO_SCOPES                                ,
                      user_login  = 'surrogate-no-scopes'                              ,
                      user_id     = 1000008                                            ,
                      scopes      = []                                                 ,
                      user_name   = 'Surrogate No Scopes User'                         ,
                      user_email  = 'no-scopes@surrogate.local'                        )
        
        # Invalid PAT
        self._add_pat(token       = self.PAT__INVALID                                  ,
                      user_login  = 'surrogate-invalid'                                ,
                      user_id     = 1000009                                            ,
                      scopes      = []                                                 ,
                      is_valid    = False                                              ,
                      user_name   = 'Surrogate Invalid User'                           ,
                      user_email  = 'invalid@surrogate.local'                          )
    
    def _add_pat(self, token           : str                        ,
                       user_login      : str                        ,
                       user_id         : int                        ,
                       scopes          : List[Enum__GitHub__Scope]  ,
                       is_valid        : bool = True                ,
                       is_expired      : bool = False               ,
                       is_rate_limited : bool = False               ,
                       user_name       : str  = None                ,
                       user_email      : str  = None                ):
        
        pat_info = Schema__Surrogate__PAT(token           = token           ,
                                          user_login      = user_login      ,
                                          user_id         = user_id         ,
                                          scopes          = scopes          ,
                                          is_valid        = is_valid        ,
                                          is_expired      = is_expired      ,
                                          is_rate_limited = is_rate_limited )
        self._pats[token] = pat_info
        
        user_info = Schema__Surrogate__User(login                     = user_login                 ,
                                            id                        = user_id                    ,
                                            name                      = user_name                  ,
                                            email                     = user_email                 ,
                                            company                   = 'Surrogate Corp'          ,
                                            created_at                = '2024-01-01T00:00:00Z'    ,
                                            public_repos              = 10                         ,
                                            total_private_repos       = 5                          ,
                                            owned_private_repos       = 5                          ,
                                            collaborators             = 3                          ,
                                            two_factor_authentication = True                       ,
                                            plan                      = dict(name          = 'enterprise'  ,
                                                                             space         = 976562499     ,
                                                                             private_repos = 999999        ))
        self._users[token] = user_info
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Convenience accessors
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def admin_pat(self) -> str:                                                 # Get admin PAT with full access
        return self.PAT__ADMIN
    
    def repo_write_pat(self) -> str:                                            # Get PAT with repo write access
        return self.PAT__REPO_WRITE
    
    def repo_read_pat(self) -> str:                                             # Get PAT with repo read-only access
        return self.PAT__REPO_READ
    
    def org_admin_pat(self) -> str:                                             # Get PAT with org admin access
        return self.PAT__ORG_ADMIN
    
    def env_only_pat(self) -> str:                                              # Get PAT with environment-only access
        return self.PAT__ENV_ONLY
    
    def expired_pat(self) -> str:                                               # Get expired PAT (returns 401)
        return self.PAT__EXPIRED
    
    def rate_limited_pat(self) -> str:                                          # Get rate-limited PAT (returns 429)
        return self.PAT__RATE_LIMITED
    
    def no_scopes_pat(self) -> str:                                             # Get PAT with no scopes (returns 403 on operations)
        return self.PAT__NO_SCOPES
    
    def invalid_pat(self) -> str:                                               # Get invalid PAT (returns 401)
        return self.PAT__INVALID
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Validation
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_pat_info(self, pat: str) -> Optional[Schema__Surrogate__PAT]:       # Get PAT definition if known
        return self._pats.get(pat)
    
    def get_user(self, pat: str) -> Optional[Schema__Surrogate__User]:          # Get user for PAT
        return self._users.get(pat)
    
    def is_known_pat(self, pat: str) -> bool:                                   # Check if PAT is known to surrogate
        return pat in self._pats
    
    def is_valid_pat(self, pat: str) -> bool:                                   # Check if PAT is valid (known and not expired/invalid)
        pat_info = self.get_pat_info(pat)
        if not pat_info:
            return False
        return pat_info.is_valid and not pat_info.is_expired
    
    def is_expired(self, pat: str) -> bool:                                     # Check if PAT is expired
        pat_info = self.get_pat_info(pat)
        return pat_info.is_expired if pat_info else False
    
    def is_rate_limited(self, pat: str) -> bool:                                # Check if PAT is rate limited
        pat_info = self.get_pat_info(pat)
        return pat_info.is_rate_limited if pat_info else False
    
    def has_scope(self, pat: str, scope: Enum__GitHub__Scope) -> bool:          # Check if PAT has specific scope
        pat_info = self.get_pat_info(pat)
        return pat_info.has_scope(scope) if pat_info else False
    
    def can_read_repo_secrets(self, pat: str) -> bool:                          # Check if PAT can read repository secrets
        pat_info = self.get_pat_info(pat)
        return pat_info.can_read_repo_secrets() if pat_info else False
    
    def can_write_repo_secrets(self, pat: str) -> bool:                         # Check if PAT can write repository secrets
        pat_info = self.get_pat_info(pat)
        return pat_info.can_write_repo_secrets() if pat_info else False
    
    def can_admin_org(self, pat: str) -> bool:                                  # Check if PAT can administer organization
        pat_info = self.get_pat_info(pat)
        return pat_info.can_admin_org() if pat_info else False
