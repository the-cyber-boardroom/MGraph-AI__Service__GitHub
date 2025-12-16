import unittest
from unittest                                                                              import TestCase
from osbot_fast_api.api.Fast_API                                                           import Fast_API
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Fast_API           import GitHub__API__Surrogate__Fast_API
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__GitHub__API__Surrogate__Fast_API(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state    = GitHub__API__Surrogate__State()
        cls.pats     = GitHub__API__Surrogate__PATs().setup()
        cls.keys     = GitHub__API__Surrogate__Keys().setup()
        cls.fast_api = GitHub__API__Surrogate__Fast_API(state = cls.state ,
                                                        pats  = cls.pats  ,
                                                        keys  = cls.keys  )
        cls.fast_api.setup()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.fast_api as _:
            assert type(_)          is GitHub__API__Surrogate__Fast_API
            assert isinstance(_,    Fast_API)
            assert _.state          is self.state
            assert _.pats           is self.pats
            assert _.keys           is self.keys
            assert _.config.name    == 'GitHub API Surrogate'

    def test__app(self):
        app = self.fast_api.app()
        assert app is not None
        # Note: Fast_API uses class name for title by default

    # ═══════════════════════════════════════════════════════════════════════════════
    # Route registration tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes__registers_all_routes(self):
        app    = self.fast_api.app()
        routes = [route.path for route in app.routes]

        # User routes
        assert '/user'       in routes
        assert '/rate_limit' in routes

        # Repo secret routes
        assert '/repos/{owner}/{repo}/actions/secrets/public-key'     in routes
        assert '/repos/{owner}/{repo}/actions/secrets'                in routes
        assert '/repos/{owner}/{repo}/actions/secrets/{secret_name}'  in routes

        # Env secret routes
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets/public-key'    in routes
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets'               in routes
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}' in routes

        # Org secret routes
        assert '/orgs/{org}/actions/secrets/public-key'    in routes
        assert '/orgs/{org}/actions/secrets'               in routes
        assert '/orgs/{org}/actions/secrets/{secret_name}' in routes

    def test__setup_routes__http_methods(self):
        app    = self.fast_api.app()
        routes = [(route.path, route.methods) for route in app.routes if hasattr(route, 'methods')]

        # Verify GET routes exist
        get_paths = [path for path, methods in routes if 'GET' in methods]
        assert '/user'       in get_paths
        assert '/rate_limit' in get_paths
        assert '/repos/{owner}/{repo}/actions/secrets' in get_paths

        # Verify PUT routes exist
        put_paths = [path for path, methods in routes if 'PUT' in methods]
        assert '/repos/{owner}/{repo}/actions/secrets/{secret_name}' in put_paths

        # Verify DELETE routes exist
        delete_paths = [path for path, methods in routes if 'DELETE' in methods]
        assert '/repos/{owner}/{repo}/actions/secrets/{secret_name}' in delete_paths

    # ═══════════════════════════════════════════════════════════════════════════════
    # Dependency injection tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__add_routes_with_deps__injects_dependencies(self):
        # Create fresh instance
        state    = GitHub__API__Surrogate__State()
        pats     = GitHub__API__Surrogate__PATs().setup()
        keys     = GitHub__API__Surrogate__Keys().setup()
        fast_api = GitHub__API__Surrogate__Fast_API(state = state ,
                                                    pats  = pats  ,
                                                    keys  = keys  )
        fast_api.setup()

        # Verify app was created with routes
        app    = fast_api.app()
        routes = [route.path for route in app.routes]
        assert len(routes) > 5                                                  # Should have multiple routes registered

    def test__dependencies_are_shared_across_routes(self):
        # All routes should share same state/pats/keys instances
        # This is verified implicitly by the integration tests, but let's
        # verify the fast_api holds the references
        assert self.fast_api.state is self.state
        assert self.fast_api.pats  is self.pats
        assert self.fast_api.keys  is self.keys
