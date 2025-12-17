from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate                      import GitHub__API__Surrogate
from mgraph_ai_service_github.service.github.GitHub__API                                    import set_session_factory, clear_session_factory
from mgraph_ai_service_github.surrogates.github.session.Requests__Session__Github__Surrogate import Requests__Session__Github__Surrogate


class GitHub__API__Surrogate__Test_Context(Type_Safe):                          # Helper to wire GitHub__API to use surrogate in tests

    surrogate : GitHub__API__Surrogate = None

    def setup(self) -> 'GitHub__API__Surrogate__Test_Context':                  # Initialize surrogate and wire into GitHub__API
        self.surrogate   = GitHub__API__Surrogate().setup()
        test_client      = self.surrogate.test_client()

        def session_factory(api_token: str):
            return Requests__Session__Github__Surrogate(api_token   = api_token   ,
                                                        test_client = test_client )

        set_session_factory(session_factory)
        return self

    def teardown(self) -> 'GitHub__API__Surrogate__Test_Context':               # Clear surrogate wiring
        clear_session_factory()
        return self

    def __enter__(self):                                                        # Context manager support
        return self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()
        return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Fluent API for test data setup (delegates to surrogate)
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_repo(self, owner: str, repo: str, private: bool = False             # Add repository
                 ) -> 'GitHub__API__Surrogate__Test_Context':
        self.surrogate.add_repo(owner, repo, private)
        return self

    def add_environment(self, owner: str, repo: str, environment: str           # Add environment to repo
                        ) -> 'GitHub__API__Surrogate__Test_Context':
        self.surrogate.add_environment(owner, repo, environment)
        return self

    def add_secret(self, owner: str, repo: str, name: str, value: str = None    # Add repo secret
                   ) -> 'GitHub__API__Surrogate__Test_Context':
        self.surrogate.add_secret(owner, repo, name, value)
        return self

    def add_env_secret(self, owner: str, repo: str, environment: str,           # Add environment secret
                       name: str, value: str = None
                       ) -> 'GitHub__API__Surrogate__Test_Context':
        self.surrogate.add_env_secret(owner, repo, environment, name, value)
        return self

    def add_org(self, org: str) -> 'GitHub__API__Surrogate__Test_Context':       # Add organization
        self.surrogate.add_org(org)
        return self

    def add_org_secret(self, org: str, name: str, value: str = None,            # Add org secret
                       visibility: str = 'private'
                       ) -> 'GitHub__API__Surrogate__Test_Context':
        self.surrogate.add_org_secret(org, name, value, visibility)
        return self

    # ═══════════════════════════════════════════════════════════════════════════════
    # PAT accessors (delegates to surrogate.pats)
    # ═══════════════════════════════════════════════════════════════════════════════

    def admin_pat(self) -> str:
        return self.surrogate.pats.admin_pat()

    def repo_write_pat(self) -> str:
        return self.surrogate.pats.repo_write_pat()

    def repo_read_pat(self) -> str:
        return self.surrogate.pats.repo_read_pat()

    def org_admin_pat(self) -> str:
        return self.surrogate.pats.org_admin_pat()

    def expired_pat(self) -> str:
        return self.surrogate.pats.expired_pat()

    def rate_limited_pat(self) -> str:
        return self.surrogate.pats.rate_limited_pat()

    def no_scopes_pat(self) -> str:
        return self.surrogate.pats.no_scopes_pat()

    def invalid_pat(self) -> str:
        return self.surrogate.pats.invalid_pat()