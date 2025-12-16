import unittest
from unittest                                                                              import TestCase
from fastapi                                                                               import FastAPI
from starlette.testclient                                                                  import TestClient
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Env_Secrets         import Routes__GitHub__Env_Secrets
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                import Routes__GitHub__Base
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__Routes__GitHub__Env_Secrets(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state  = GitHub__API__Surrogate__State()
        cls.pats   = GitHub__API__Surrogate__PATs().setup()
        cls.keys   = GitHub__API__Surrogate__Keys().setup()
        cls.app    = FastAPI()
        cls.routes = Routes__GitHub__Env_Secrets(app   = cls.app   ,
                                                 state = cls.state ,
                                                 pats  = cls.pats  ,
                                                 keys  = cls.keys  )
        cls.routes.setup()
        cls.client = TestClient(cls.app, raise_server_exceptions=False)

    def setUp(self):
        self.state.reset()
        self.keys.reset()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.routes as _:
            assert type(_)       is Routes__GitHub__Env_Secrets
            assert isinstance(_, Routes__GitHub__Base)

    def test__setup_routes__registers_env_secret_routes(self):
        routes = [route.path for route in self.app.routes]
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets/public-key'    in routes
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets'               in routes
        assert '/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}' in routes

    # ═══════════════════════════════════════════════════════════════════════════════
    # Helper to setup repo with environment
    # ═══════════════════════════════════════════════════════════════════════════════

    def _setup_repo_with_env(self, owner='test-owner', repo='test-repo', env='production'):
        self.state.add_repo(owner, repo)
        self.state.add_environment(owner, repo, env)
        return owner, repo, env

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET public-key tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_env_public_key__success(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert 'key_id' in data
        assert 'key'    in data

    def test__get_env_public_key__repo_not_found(self):
        response = self.client.get('/repos/nonexistent/repo/environments/prod/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__get_env_public_key__env_not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/environments/nonexistent/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__get_env_public_key__no_auth(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets/public-key')

        assert response.status_code == 401

    def test__get_env_public_key__no_permission(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.no_scopes_pat()}'})

        assert response.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /environments/{env}/secrets (list) tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_env_secrets__empty(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 0
        assert data['secrets']     == []

    def test__list_env_secrets__with_secrets(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret(owner, repo, env, 'ENV_API_KEY', encrypted, key_id)
        self.state.set_env_secret(owner, repo, env, 'ENV_DB_PASS', encrypted, key_id)

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 2
        names = [s['name'] for s in data['secrets']]
        assert 'ENV_API_KEY' in names
        assert 'ENV_DB_PASS' in names

    def test__list_env_secrets__repo_not_found(self):
        response = self.client.get('/repos/nonexistent/repo/environments/prod/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__list_env_secrets__env_not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/environments/nonexistent/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /environments/{env}/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_env_secret__success(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret(owner, repo, env, 'MY_SECRET', encrypted, key_id)

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets/MY_SECRET',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'MY_SECRET'

    def test__get_env_secret__not_found(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.get(f'/repos/{owner}/{repo}/environments/{env}/secrets/NONEXISTENT',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__get_env_secret__env_not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.get('/repos/test-owner/test-repo/environments/nonexistent/secrets/SECRET',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # PUT /environments/{env}/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__put_env_secret__create(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)

        response = self.client.put(f'/repos/{owner}/{repo}/environments/{env}/secrets/NEW_SECRET',
                                   json={'encrypted_value': encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 201
        assert self.state.get_env_secret(owner, repo, env, 'NEW_SECRET') is not None

    def test__put_env_secret__update(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'old')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret(owner, repo, env, 'EXISTING', encrypted, key_id)

        new_encrypted = self.keys.encrypt_secret(scope_id, 'new')
        response = self.client.put(f'/repos/{owner}/{repo}/environments/{env}/secrets/EXISTING',
                                   json={'encrypted_value': new_encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 204                                      # Updated

    def test__put_env_secret__env_not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.put('/repos/test-owner/test-repo/environments/nonexistent/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__put_env_secret__no_write_permission(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.put(f'/repos/{owner}/{repo}/environments/{env}/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.repo_read_pat()}'})

        assert response.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # DELETE /environments/{env}/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_env_secret__success(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret(owner, repo, env, 'TO_DELETE', encrypted, key_id)

        response = self.client.delete(f'/repos/{owner}/{repo}/environments/{env}/secrets/TO_DELETE',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 204
        assert self.state.get_env_secret(owner, repo, env, 'TO_DELETE') is None

    def test__delete_env_secret__not_found(self):
        owner, repo, env = self._setup_repo_with_env()

        response = self.client.delete(f'/repos/{owner}/{repo}/environments/{env}/secrets/NONEXISTENT',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__delete_env_secret__env_not_found(self):
        self.state.add_repo('test-owner', 'test-repo')

        response = self.client.delete('/repos/test-owner/test-repo/environments/nonexistent/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 404

    def test__delete_env_secret__no_write_permission(self):
        owner, repo, env = self._setup_repo_with_env()
        scope_id  = self.keys.scope_id_for_env(owner, repo, env)
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret(owner, repo, env, 'SECRET', encrypted, key_id)

        response = self.client.delete(f'/repos/{owner}/{repo}/environments/{env}/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.repo_read_pat()}'})

        assert response.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # Multiple environments tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__multiple_environments__isolated_secrets(self):
        self.state.add_repo('test-owner', 'test-repo')
        self.state.add_environment('test-owner', 'test-repo', 'production')
        self.state.add_environment('test-owner', 'test-repo', 'staging')

        # Add secret to production
        scope_id  = self.keys.scope_id_for_env('test-owner', 'test-repo', 'production')
        encrypted = self.keys.encrypt_secret(scope_id, 'prod_value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_env_secret('test-owner', 'test-repo', 'production', 'PROD_SECRET', encrypted, key_id)

        # Verify production has the secret
        response = self.client.get('/repos/test-owner/test-repo/environments/production/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})
        assert response.json()['total_count'] == 1

        # Verify staging does not have the secret
        response = self.client.get('/repos/test-owner/test-repo/environments/staging/secrets',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})
        assert response.json()['total_count'] == 0