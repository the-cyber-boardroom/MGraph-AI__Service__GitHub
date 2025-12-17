from unittest                                                                              import TestCase
from fastapi                                                                               import FastAPI
from starlette.testclient                                                                  import TestClient
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Repo_Secrets        import Routes__GitHub__Repo_Secrets
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                import Routes__GitHub__Base
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__Routes__GitHub__Repo_Secrets(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state  = GitHub__API__Surrogate__State()
        cls.pats   = GitHub__API__Surrogate__PATs().setup()
        cls.keys   = GitHub__API__Surrogate__Keys().setup()
        cls.app    = FastAPI()
        cls.routes = Routes__GitHub__Repo_Secrets(app   = cls.app   ,
                                                  state = cls.state ,
                                                  pats  = cls.pats  ,
                                                  keys  = cls.keys  )
        cls.routes.setup()
        cls.client = TestClient(cls.app, raise_server_exceptions=False)

    def setUp(self):
        self.state.reset()                                                      # Reset state before each test
        self.keys.reset()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.routes as _:
            assert type(_)       is Routes__GitHub__Repo_Secrets
            assert isinstance(_, Routes__GitHub__Base)

    def test__setup_routes__registers_repo_secret_routes(self):
        routes = [route.path for route in self.app.routes]
        assert '/repos/{owner}/{repo}/actions/secrets/public-key'    in routes
        assert '/repos/{owner}/{repo}/actions/secrets'               in routes
        assert '/repos/{owner}/{repo}/actions/secrets/{secret_name}' in routes

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET public-key tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_repo_public_key__success(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert 'key_id' in data
        assert 'key'    in data
        assert len(data['key']) > 0                                             # Base64-encoded public key

    def test__get_repo_public_key__repo_not_found(self):
        response = self.client.get('/repos/nonexistent/repo/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404
        assert response.json()['message'] == 'Not Found'

    def test__get_repo_public_key__no_auth(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/public-key')

        assert response.status_code == 401

    def test__get_repo_public_key__no_permission(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.no_scopes_pat()}'})

        assert response.status_code == 403

    def test__get_repo_public_key__read_only_allowed(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.repo_read_pat()}'})

        assert response.status_code == 200

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /actions/secrets (list) tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_repo_secrets__empty(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 0
        assert data['secrets']     == []

    def test__list_repo_secrets__with_secrets(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'secret_value')
        key_id = self.keys.get_key_id(scope_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'API_KEY', encrypted, key_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'DB_PASS', encrypted, key_id)

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 2
        names = [s['name'] for s in data['secrets']]
        assert 'API_KEY' in names
        assert 'DB_PASS' in names

    def test__list_repo_secrets__repo_not_found(self):
        response = self.client.get('/repos/nonexistent/repo/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__list_repo_secrets__no_permission(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.no_scopes_pat()}'})

        assert response.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_repo_secret__success(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'secret_value')
        key_id = self.keys.get_key_id(scope_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'API_KEY', encrypted, key_id)

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/API_KEY',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'API_KEY'
        assert 'created_at' in data
        assert 'updated_at' in data

    def test__get_repo_secret__not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/actions/secrets/NONEXISTENT',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__get_repo_secret__repo_not_found(self):
        response = self.client.get('/repos/nonexistent/repo/actions/secrets/API_KEY',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # PUT /actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__put_repo_secret__create(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id  = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'secret_value')
        key_id    = self.keys.get_key_id(scope_id)

        response = self.client.put('/repos/test-owner/test-repo/actions/secrets/NEW_SECRET',
                                   json={'encrypted_value': encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 201                                      # Created
        assert self.state.get_repo_secret('test-owner', 'test-repo', 'NEW_SECRET') is not None

    def test__put_repo_secret__update(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id  = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'old_value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'EXISTING', encrypted, key_id)

        new_encrypted = self.keys.encrypt_secret(scope_id, 'new_value')
        response = self.client.put('/repos/test-owner/test-repo/actions/secrets/EXISTING',
                                   json={'encrypted_value': new_encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 204                                      # No Content (updated)

    def test__put_repo_secret__repo_not_found(self):
        response = self.client.put('/repos/nonexistent/repo/actions/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__put_repo_secret__no_write_permission(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.put('/repos/test-owner/test-repo/actions/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.repo_read_pat()}'})

        assert response.status_code == 403

    def test__put_repo_secret__write_allowed_with_repo_write(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id  = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)

        response = self.client.put('/repos/test-owner/test-repo/actions/secrets/SECRET',
                                   json={'encrypted_value': encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 201

    # ═══════════════════════════════════════════════════════════════════════════════
    # DELETE /actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_repo_secret__success(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id  = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'TO_DELETE', encrypted, key_id)

        response = self.client.delete('/repos/test-owner/test-repo/actions/secrets/TO_DELETE',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 204
        assert self.state.get_repo_secret('test-owner', 'test-repo', 'TO_DELETE') is None

    def test__delete_repo_secret__not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.delete('/repos/test-owner/test-repo/actions/secrets/NONEXISTENT',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__delete_repo_secret__repo_not_found(self):
        response = self.client.delete('/repos/nonexistent/repo/actions/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__delete_repo_secret__no_write_permission(self):
        self.state.add_repo('test-owner', 'test-repo')
        scope_id  = self.keys.scope_id_for_repo('test-owner', 'test-repo')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_repo_secret('test-owner', 'test-repo', 'SECRET', encrypted, key_id)

        response = self.client.delete('/repos/test-owner/test-repo/actions/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.repo_read_pat()}'})

        assert response.status_code == 403