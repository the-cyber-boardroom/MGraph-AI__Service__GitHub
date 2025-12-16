from osbot_fast_api.api.Fast_API                                                           import Fast_API
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__User                import Routes__GitHub__User
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Repo_Secrets        import Routes__GitHub__Repo_Secrets
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Env_Secrets         import Routes__GitHub__Env_Secrets
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Org_Secrets         import Routes__GitHub__Org_Secrets
from mgraph_ai_service_github.utils.Version                                                import version__mgraph_ai_service_github


class GitHub__API__Surrogate__Fast_API(Fast_API):                               # FastAPI application for GitHub API surrogate

    state : GitHub__API__Surrogate__State  = None                               # In-memory state (set externally)
    pats  : GitHub__API__Surrogate__PATs   = None                               # PAT manager (set externally)
    keys  : GitHub__API__Surrogate__Keys   = None                               # Key manager (set externally)

    def setup(self):                                                                        # Configure FastAPI application settings
        with self.config as _:
            _.name    = 'GitHub API Surrogate'
            _.version = version__mgraph_ai_service_github

        return super().setup()

    def add_routes_with_deps(self, routes_class):                               # Add routes with injected dependencies
        routes = routes_class(app   = self.app() ,
                              state = self.state ,
                              pats  = self.pats  ,
                              keys  = self.keys  )
        routes.setup()
        return self

    def setup_routes(self):                                                     # Register all route classes
        self.add_routes_with_deps(Routes__GitHub__User        )
        self.add_routes_with_deps(Routes__GitHub__Repo_Secrets)
        self.add_routes_with_deps(Routes__GitHub__Env_Secrets )
        self.add_routes_with_deps(Routes__GitHub__Org_Secrets )
        return self
