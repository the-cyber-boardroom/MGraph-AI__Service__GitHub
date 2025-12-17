from unittest                                                                              import TestCase
from fastapi                                                                               import FastAPI
from starlette.testclient                                                                  import TestClient
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__User                import Routes__GitHub__User
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                import Routes__GitHub__Base
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__Routes__GitHub__User(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state  = GitHub__API__Surrogate__State()
        cls.pats   = GitHub__API__Surrogate__PATs().setup()
        cls.keys   = GitHub__API__Surrogate__Keys().setup()
        cls.app    = FastAPI()
        cls.routes = Routes__GitHub__User(app   = cls.app   ,
                                          state = cls.state ,
                                          pats  = cls.pats  ,
                                          keys  = cls.keys  )
        cls.routes.setup()
        cls.client = TestClient(cls.app, raise_server_exceptions=False)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.routes as _:
            assert type(_)       is Routes__GitHub__User
            assert isinstance(_, Routes__GitHub__Base)
            assert _.state       is self.state
            assert _.pats        is self.pats
            assert _.keys        is self.keys

    def test__setup_routes__registers_user_routes(self):
        routes = [route.path for route in self.app.routes]
        assert '/user'       in routes
        assert '/rate_limit' in routes

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /user tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__user__valid_admin_token(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['login'] == 'surrogate-admin'
        assert data['id']    == 1000001
        assert data['name']  == 'Surrogate Admin User'
        assert data['email'] == 'admin@surrogate.local'

    def test__user__valid_repo_write_token(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['login'] == 'surrogate-repo-write'

    def test__user__bearer_format(self):
        response = self.client.get('/user', headers={'Authorization': f'Bearer {self.pats.admin_pat()}'})

        assert response.status_code == 200
        assert response.json()['login'] == 'surrogate-admin'

    def test__user__no_auth(self):
        response = self.client.get('/user')

        assert response.status_code == 401
        assert response.json()['message'] == 'Requires authentication'

    def test__user__invalid_token(self):
        response = self.client.get('/user', headers={'Authorization': 'token invalid_token'})

        assert response.status_code == 401
        assert response.json()['message'] == 'Bad credentials'

    def test__user__expired_token(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.expired_pat()}'})

        assert response.status_code == 401
        assert response.json()['message'] == 'Bad credentials'

    def test__user__rate_limited_token(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.rate_limited_pat()}'})

        assert response.status_code == 429
        assert 'rate limit' in response.json()['message']

    def test__user__response_includes_plan(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.admin_pat()}'})

        data = response.json()
        assert 'plan' in data
        assert data['plan']['name'] == 'enterprise'

    def test__user__response_includes_2fa(self):
        response = self.client.get('/user', headers={'Authorization': f'token {self.pats.admin_pat()}'})

        data = response.json()
        assert data['two_factor_authentication'] is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /rate_limit tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__rate_limit__valid_token(self):
        response = self.client.get('/rate_limit', headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert 'rate' in data
        assert data['rate']['limit']     == 5000
        assert data['rate']['remaining'] == 4999
        assert 'reset' in data['rate']
        assert 'used'  in data['rate']

    def test__rate_limit__no_auth(self):
        response = self.client.get('/rate_limit')

        assert response.status_code == 401

    def test__rate_limit__invalid_token(self):
        response = self.client.get('/rate_limit', headers={'Authorization': 'token invalid'})

        assert response.status_code == 401

    def test__rate_limit__rate_limited_token(self):
        response = self.client.get('/rate_limit', headers={'Authorization': f'token {self.pats.rate_limited_pat()}'})

        assert response.status_code == 429
