from typing                                                                           import Dict, Optional, List
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Repo       import Schema__Surrogate__Repo
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Secret     import Schema__Surrogate__Secret, Schema__Surrogate__Org__Secret
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Public_Key import Schema__Surrogate__Public_Key
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Rate_Limit import Schema__Surrogate__Rate_Limit


class GitHub__API__Surrogate__State(Type_Safe):                                 # In-memory state for the GitHub API surrogate

    repos          : Dict[str, Schema__Surrogate__Repo]                         # Repository data indexed by "owner/repo"
    
    # Secrets by scope
    secrets__repo  : Dict[str, Dict[str, Schema__Surrogate__Secret]]            # "owner/repo" -> {name -> secret}
    secrets__env   : Dict[str, Dict[str, Dict[str, Schema__Surrogate__Secret]]] # "owner/repo" -> {env -> {name -> secret}}
    secrets__org   : Dict[str, Dict[str, Schema__Surrogate__Org__Secret]]       # "org" -> {name -> secret}
    
    # Public keys for encryption (generated per scope)
    public_keys    : Dict[str, Schema__Surrogate__Public_Key]                   # scope_id -> public key
    
    # Rate limit tracking per PAT
    rate_limits    : Dict[str, Schema__Surrogate__Rate_Limit]                   # PAT -> rate limit

    def reset(self) -> 'GitHub__API__Surrogate__State':                         # Clear all state for test isolation
        self.repos         = {}                                                 # todo: see if this works, since Type_Safe might prevent this assigment
        self.secrets__repo = {}                                                 #       we might be better off clearing the dict directly
        self.secrets__env  = {}
        self.secrets__org  = {}
        self.public_keys   = {}
        self.rate_limits   = {}
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Repository operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def _repo_key(self, owner: str, repo: str) -> str:                          # Generate repo key
        return f"{owner}/{repo}"
    
    def add_repo(self, owner        : str             ,                         # Add a repository to state
                       repo         : str             ,
                       private      : bool  = False   ,
                       environments : List[str] = None
                 ) -> 'GitHub__API__Surrogate__State':
        repo_key  = self._repo_key(owner, repo)
        repo_data = Schema__Surrogate__Repo(owner        = owner                   ,
                                            name         = repo                    ,
                                            full_name    = repo_key                ,
                                            private      = private                 ,
                                            environments = environments or []      )
        self.repos[repo_key]         = repo_data
        self.secrets__repo[repo_key] = {}                                       # Initialize empty secrets dict
        self.secrets__env[repo_key]  = {}                                       # Initialize empty env secrets dict
        return self
    
    def get_repo(self, owner: str, repo: str) -> Optional[Schema__Surrogate__Repo]:
        return self.repos.get(self._repo_key(owner, repo))
    
    def repo_exists(self, owner: str, repo: str) -> bool:                       # Check if repository exists
        return self._repo_key(owner, repo) in self.repos
    
    def add_environment(self, owner: str,
                              repo: str,
                              environment: str           # Add an environment to a repository
                        ) -> 'GitHub__API__Surrogate__State':
        repo_key  = self._repo_key(owner, repo)
        repo_data = self.repos.get(repo_key)
        if repo_data and environment not in repo_data.environments:
            repo_data.environments.append(environment)
            if repo_key not in self.secrets__env:
                self.secrets__env[repo_key] = {}
            if environment not in self.secrets__env[repo_key]:
                self.secrets__env[repo_key][environment] = {}
        return self
    
    def environment_exists(self, owner: str, repo: str, environment: str) -> bool:
        repo_data = self.get_repo(owner, repo)
        return repo_data is not None and environment in repo_data.environments
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Repository secret operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def list_repo_secrets(self, owner: str, repo: str                           # List all repository secrets
                          ) -> List[Schema__Surrogate__Secret]:
        repo_key = self._repo_key(owner, repo)
        secrets  = self.secrets__repo.get(repo_key, {})
        return list(secrets.values())
    
    def get_repo_secret(self, owner: str, repo: str, name: str                  # Get a repository secret
                        ) -> Optional[Schema__Surrogate__Secret]:
        repo_key = self._repo_key(owner, repo)
        secrets  = self.secrets__repo.get(repo_key, {})
        return secrets.get(name)
    
    def set_repo_secret(self, owner           : str ,                           # Create or update repository secret
                              repo            : str ,
                              name            : str ,
                              encrypted_value : str ,
                              key_id          : str
                        ) -> bool:
        repo_key = self._repo_key(owner, repo)
        if repo_key not in self.secrets__repo:
            self.secrets__repo[repo_key] = {}
        
        existing = self.secrets__repo[repo_key].get(name)
        now      = '2024-01-15T10:30:00Z'                                       # Fixed timestamp for testing
        
        if existing:
            existing.encrypted_value = encrypted_value
            existing.key_id          = key_id
            existing.updated_at      = now
        else:
            secret = Schema__Surrogate__Secret(name            = name            ,
                                               created_at      = now             ,
                                               updated_at      = now             ,
                                               encrypted_value = encrypted_value ,
                                               key_id          = key_id          )
            self.secrets__repo[repo_key][name] = secret
        return True
    
    def delete_repo_secret(self, owner: str, repo: str, name: str               # Delete repository secret
                           ) -> bool:                                            # Returns True if existed
        repo_key = self._repo_key(owner, repo)
        secrets  = self.secrets__repo.get(repo_key, {})
        if name in secrets:
            del secrets[name]
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Environment secret operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def list_env_secrets(self, owner: str, repo: str, environment: str          # List all environment secrets
                         ) -> List[Schema__Surrogate__Secret]:
        repo_key    = self._repo_key(owner, repo)
        env_secrets = self.secrets__env.get(repo_key, {}).get(environment, {})
        return list(env_secrets.values())
    
    def get_env_secret(self, owner: str, repo: str, environment: str, name: str # Get an environment secret
                       ) -> Optional[Schema__Surrogate__Secret]:
        repo_key    = self._repo_key(owner, repo)
        env_secrets = self.secrets__env.get(repo_key, {}).get(environment, {})
        return env_secrets.get(name)
    
    def set_env_secret(self, owner           : str ,                            # Create or update environment secret
                             repo            : str ,
                             environment     : str ,
                             name            : str ,
                             encrypted_value : str ,
                             key_id          : str
                       ) -> bool:
        repo_key = self._repo_key(owner, repo)
        if repo_key not in self.secrets__env:
            self.secrets__env[repo_key] = {}
        if environment not in self.secrets__env[repo_key]:
            self.secrets__env[repo_key][environment] = {}
        
        existing = self.secrets__env[repo_key][environment].get(name)
        now      = '2024-01-15T10:30:00Z'
        
        if existing:
            existing.encrypted_value = encrypted_value
            existing.key_id          = key_id
            existing.updated_at      = now
        else:
            secret = Schema__Surrogate__Secret(name            = name            ,
                                               created_at      = now             ,
                                               updated_at      = now             ,
                                               encrypted_value = encrypted_value ,
                                               key_id          = key_id          )
            self.secrets__env[repo_key][environment][name] = secret
        return True
    
    def delete_env_secret(self, owner: str, repo: str, environment: str, name: str
                          ) -> bool:
        repo_key    = self._repo_key(owner, repo)
        env_secrets = self.secrets__env.get(repo_key, {}).get(environment, {})
        if name in env_secrets:
            del env_secrets[name]
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Organization secret operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def add_org(self, org: str) -> 'GitHub__API__Surrogate__State':             # Add an organization
        if org not in self.secrets__org:
            self.secrets__org[org] = {}
        return self
    
    def org_exists(self, org: str) -> bool:                                     # Check if organization exists
        return org in self.secrets__org
    
    def list_org_secrets(self, org: str                                         # List all organization secrets
                         ) -> List[Schema__Surrogate__Org__Secret]:
        secrets = self.secrets__org.get(org, {})
        return list(secrets.values())
    
    def get_org_secret(self, org: str, name: str                                # Get an organization secret
                       ) -> Optional[Schema__Surrogate__Org__Secret]:
        secrets = self.secrets__org.get(org, {})
        return secrets.get(name)
    
    def set_org_secret(self, org             : str                 ,            # Create or update organization secret
                             name            : str                 ,
                             encrypted_value : str                 ,
                             key_id          : str                 ,
                             visibility      : str   = 'private'
                       ) -> bool:
        if org not in self.secrets__org:
            self.secrets__org[org] = {}
        
        existing = self.secrets__org[org].get(name)
        now      = '2024-01-15T10:30:00Z'
        
        if existing:
            existing.encrypted_value = encrypted_value
            existing.key_id          = key_id
            existing.visibility      = visibility
            existing.updated_at      = now
        else:
            secret = Schema__Surrogate__Org__Secret(name            = name            ,
                                                    created_at      = now             ,
                                                    updated_at      = now             ,
                                                    visibility      = visibility      ,
                                                    encrypted_value = encrypted_value ,
                                                    key_id          = key_id          )
            self.secrets__org[org][name] = secret
        return True
    
    def delete_org_secret(self, org: str, name: str) -> bool:                   # Delete organization secret
        secrets = self.secrets__org.get(org, {})
        if name in secrets:
            del secrets[name]
            return True
        return False
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Public key operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def set_public_key(self, scope_id   : str                      ,            # Store public key for scope
                             public_key : Schema__Surrogate__Public_Key
                       ) -> None:
        self.public_keys[scope_id] = public_key
    
    def get_public_key(self, scope_id: str                                      # Get public key for scope
                       ) -> Optional[Schema__Surrogate__Public_Key]:
        return self.public_keys.get(scope_id)
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Rate limit operations
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_rate_limit(self, pat: str) -> Schema__Surrogate__Rate_Limit:        # Get or create rate limit for PAT
        if pat not in self.rate_limits:
            self.rate_limits[pat] = Schema__Surrogate__Rate_Limit()
        return self.rate_limits[pat]
