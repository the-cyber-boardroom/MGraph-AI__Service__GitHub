from typing                                                                        import Optional
from fastapi                                                                       import FastAPI
from starlette.testclient                                                          import TestClient
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from mgraph_ai_service_github.service.github.GitHub__API                           import GitHub__API
from mgraph_ai_service_github.service.github.GitHub__Secrets import GitHub__Secrets
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State      import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs       import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys       import GitHub__API__Surrogate__Keys
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Session    import GitHub__API__Surrogate__Session
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Routes     import GitHub__API__Surrogate__Routes


class GitHub__API__Surrogate(Type_Safe):                                        # Main surrogate orchestrator - creates FastAPI app mocking api.github.com
    
    state   : GitHub__API__Surrogate__State
    pats    : GitHub__API__Surrogate__PATs
    keys    : GitHub__API__Surrogate__Keys
    routes  : GitHub__API__Surrogate__Routes
    _app    : FastAPI                        = None
    _client : TestClient                     = None
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Lifecycle
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def setup(self) -> 'GitHub__API__Surrogate':                                # Initialize all components and create FastAPI app
        self.state  = GitHub__API__Surrogate__State ()
        self.pats   = GitHub__API__Surrogate__PATs  ().setup()
        self.keys   = GitHub__API__Surrogate__Keys  ().setup()
        self.routes = GitHub__API__Surrogate__Routes(state = self.state ,
                                                     pats  = self.pats  ,
                                                     keys  = self.keys  )
        self._app    = self.routes.create_app()
        self._client = TestClient(self._app, raise_server_exceptions=False)
        return self
    
    def reset(self) -> 'GitHub__API__Surrogate':                                # Reset all state for test isolation
        self.state.reset()
        self.keys.reset()
        return self
    
    def app(self) -> FastAPI:                                                   # Get the FastAPI application
        return self._app
    
    def test_client(self) -> TestClient:                                        # Get TestClient for the app
        return self._client
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Injection Methods
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def create_session(self ,                                           # Create a session configured for this surrogate
                       pat  : str = None                                # PAT to use for Authorization header. If None, uses admin PAT.
                  ) -> GitHub__API__Surrogate__Session:                 # Session configured with authorization header

        if pat is None:
            pat = self.pats.admin_pat()
        
        session = GitHub__API__Surrogate__Session(test_client = self._client)
        session.headers.update({'Authorization': f'token {pat}'})
        return session
    
    def create_api(self,                                                # Create a GitHub__API instance wired to this surrogate
                   pat : str = None                                     # PAT to use. If None, uses admin PAT.
              ) -> GitHub__API:                                         # GitHub__API with session pointing to surrogate
        
        if pat is None:
            pat = self.pats.admin_pat()
        
        github_api = GitHub__API(api_token=pat)
        return self.inject(github_api)
    
    def inject(self,                                                                        # Replace session on existing GitHub__API instance
               github_api: GitHub__API                                                      #  Existing instance to modify
          ) -> GitHub__API:                                                                  # Returns Same instance with session replaced
        session = self.create_session(github_api.api_token)
        
        # Get the cache manager from the @cache_on_self decorator
        # The session() method must be called first to initialize the cache

        github_api.session()                                                        # Initialize cache if not already done
        
        cache_manager = github_api.session(__return__='cache_on_self')
        storage       = cache_manager.cache_storage
        key           = cache_manager.no_args_key

        storage.set_cached_value(github_api, key, session)                          # Replace the cached session with our surrogate session
        
        return github_api
    
    def create_secrets(self, pat: str = None, repo_name: str = None                 # Create a GitHub__Secrets instance wired to this surrogate
                       ) -> GitHub__Secrets:
        """Create a GitHub__Secrets instance wired to this surrogate
        
        Args:
            pat: PAT to use. If None, uses admin PAT.
            repo_name: Repository name in "owner/repo" format
            
        Returns:
            GitHub__Secrets with API pointing to surrogate
        """
        
        if pat is None:
            pat = self.pats.admin_pat()
        
        if repo_name is None:
            repo_name = "test-owner/test-repo"
        
        github_secrets = GitHub__Secrets(api_token = pat       ,
                                         repo_name = repo_name )
        self.inject(github_secrets.api)
        return github_secrets
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Fluent Test Data Helpers
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def add_repo(self, owner: str, repo: str, private: bool = False             # Add a repository to state
                 ) -> 'GitHub__API__Surrogate':
        self.state.add_repo(owner, repo, private)
        return self
    
    def add_environment(self, owner: str, repo: str, environment: str           # Add an environment to a repository
                        ) -> 'GitHub__API__Surrogate':
        self.state.add_environment(owner, repo, environment)
        return self
    
    def add_secret(self, owner: str, repo: str, name: str, value: str = None    # Add a repository secret
                   ) -> 'GitHub__API__Surrogate':
        # Generate encrypted value if needed
        scope_id = self.keys.scope_id_for_repo(owner, repo)
        if value is None:
            value = f"secret_value_for_{name}"
        encrypted_value = self.keys.encrypt_secret(scope_id, value)
        key_id          = self.keys.get_key_id(scope_id)
        
        self.state.set_repo_secret(owner, repo, name, encrypted_value, key_id)
        return self
    
    def add_env_secret(self, owner: str, repo: str, environment: str,           # Add an environment secret
                       name: str, value: str = None
                       ) -> 'GitHub__API__Surrogate':
        scope_id = self.keys.scope_id_for_env(owner, repo, environment)
        if value is None:
            value = f"secret_value_for_{name}"
        encrypted_value = self.keys.encrypt_secret(scope_id, value)
        key_id          = self.keys.get_key_id(scope_id)
        
        self.state.set_env_secret(owner, repo, environment, name, encrypted_value, key_id)
        return self
    
    def add_org(self, org: str) -> 'GitHub__API__Surrogate':                    # Add an organization
        self.state.add_org(org)
        return self
    
    def add_org_secret(self, org: str, name: str, value: str = None,            # Add an organization secret
                       visibility: str = 'private'
                       ) -> 'GitHub__API__Surrogate':
        scope_id = self.keys.scope_id_for_org(org)
        if value is None:
            value = f"secret_value_for_{name}"
        encrypted_value = self.keys.encrypt_secret(scope_id, value)
        key_id          = self.keys.get_key_id(scope_id)
        
        self.state.set_org_secret(org, name, encrypted_value, key_id, visibility)
        return self
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Convenience methods for encryption
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def encrypt_for_repo(self, owner: str, repo: str, value: str) -> str:       # Encrypt a value for repository secrets
        scope_id = self.keys.scope_id_for_repo(owner, repo)
        return self.keys.encrypt_secret(scope_id, value)
    
    def encrypt_for_env(self, owner: str, repo: str, environment: str,          # Encrypt a value for environment secrets
                        value: str) -> str:
        scope_id = self.keys.scope_id_for_env(owner, repo, environment)
        return self.keys.encrypt_secret(scope_id, value)
    
    def encrypt_for_org(self, org: str, value: str) -> str:                     # Encrypt a value for organization secrets
        scope_id = self.keys.scope_id_for_org(org)
        return self.keys.encrypt_secret(scope_id, value)
    
    def get_repo_key_id(self, owner: str, repo: str) -> Optional[str]:          # Get key ID for repository
        scope_id = self.keys.scope_id_for_repo(owner, repo)
        # Ensure key exists
        self.keys.get_or_create_key_pair(scope_id)
        return self.keys.get_key_id(scope_id)
    
    def get_env_key_id(self, owner: str, repo: str, environment: str            # Get key ID for environment
                       ) -> Optional[str]:
        scope_id = self.keys.scope_id_for_env(owner, repo, environment)
        self.keys.get_or_create_key_pair(scope_id)
        return self.keys.get_key_id(scope_id)
    
    def get_org_key_id(self, org: str) -> Optional[str]:                        # Get key ID for organization
        scope_id = self.keys.scope_id_for_org(org)
        self.keys.get_or_create_key_pair(scope_id)
        return self.keys.get_key_id(scope_id)
