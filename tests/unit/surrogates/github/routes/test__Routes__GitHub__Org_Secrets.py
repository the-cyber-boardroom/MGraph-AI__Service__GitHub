import unittest
from unittest                                                                              import TestCase
from fastapi                                                                               import FastAPI
from starlette.testclient                                                                  import TestClient
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Org_Secrets         import Routes__GitHub__Org_Secrets
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                import Routes__GitHub__Base
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__Routes__GitHub__Org_Secrets(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state  = GitHub__API__Surrogate__State()
        cls.pats   = GitHub__API__Surrogate__PATs().setup()
        cls.keys   = GitHub__API__Surrogate__Keys().setup()
        cls.app    = FastAPI()
        cls.routes = Routes__GitHub__Org_Secrets(app   = cls.app   ,
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
            assert type(_)       is Routes__GitHub__Org_Secrets
            assert isinstance(_, Routes__GitHub__Base)

    def test__setup_routes__registers_org_secret_routes(self):
        routes = [route.path for route in self.app.routes]
        assert '/orgs/{org}/actions/secrets/public-key'    in routes
        assert '/orgs/{org}/actions/secrets'               in routes
        assert '/orgs/{org}/actions/secrets/{secret_name}' in routes

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET public-key tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_org_public_key__success(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert 'key_id' in data
        assert 'key'    in data

    def test__get_org_public_key__org_not_found(self):
        response = self.client.get('/orgs/nonexistent/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__get_org_public_key__no_auth(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets/public-key')

        assert response.status_code == 401

    def test__get_org_public_key__no_org_admin(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 403

    def test__get_org_public_key__admin_pat_allowed(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets/public-key',
                                   headers={'Authorization': f'token {self.pats.admin_pat()}'})

        assert response.status_code == 200                                      # Admin has org admin scope

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /orgs/{org}/actions/secrets (list) tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list_org_secrets__empty(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 0
        assert data['secrets']     == []

    def test__list_org_secrets__with_secrets(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'ORG_API_KEY', encrypted, key_id)
        self.state.set_org_secret('test-org', 'ORG_DB_PASS', encrypted, key_id)

        response = self.client.get('/orgs/test-org/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] == 2
        names = [s['name'] for s in data['secrets']]
        assert 'ORG_API_KEY' in names
        assert 'ORG_DB_PASS' in names

    def test__list_org_secrets__org_not_found(self):
        response = self.client.get('/orgs/nonexistent/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__list_org_secrets__no_permission(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 403

    def test__list_org_secrets__includes_visibility(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'PUBLIC_SECRET', encrypted, key_id, visibility='all')

        response = self.client.get('/orgs/test-org/actions/secrets',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        data    = response.json()
        secret  = data['secrets'][0]
        assert secret['visibility'] == 'all'

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /orgs/{org}/actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_org_secret__success(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'MY_SECRET', encrypted, key_id)

        response = self.client.get('/orgs/test-org/actions/secrets/MY_SECRET',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'MY_SECRET'
        assert 'visibility' in data

    def test__get_org_secret__not_found(self):
        self.state.add_org('test-org')

        response = self.client.get('/orgs/test-org/actions/secrets/NONEXISTENT',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__get_org_secret__org_not_found(self):
        response = self.client.get('/orgs/nonexistent/actions/secrets/SECRET',
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # PUT /orgs/{org}/actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__put_org_secret__create(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)

        response = self.client.put('/orgs/test-org/actions/secrets/NEW_SECRET',
                                   json={'encrypted_value': encrypted, 'key_id': key_id, 'visibility': 'private'},
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 201
        assert self.state.get_org_secret('test-org', 'NEW_SECRET') is not None

    def test__put_org_secret__create_with_visibility(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)

        response = self.client.put('/orgs/test-org/actions/secrets/VISIBLE_SECRET',
                                   json={'encrypted_value': encrypted, 'key_id': key_id, 'visibility': 'all'},
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 201
        secret = self.state.get_org_secret('test-org', 'VISIBLE_SECRET')
        assert secret.visibility == 'all'

    def test__put_org_secret__update(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'old')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'EXISTING', encrypted, key_id)

        new_encrypted = self.keys.encrypt_secret(scope_id, 'new')
        response = self.client.put('/orgs/test-org/actions/secrets/EXISTING',
                                   json={'encrypted_value': new_encrypted, 'key_id': key_id},
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 204                                      # Updated

    def test__put_org_secret__org_not_found(self):
        response = self.client.put('/orgs/nonexistent/actions/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__put_org_secret__no_permission(self):
        self.state.add_org('test-org')

        response = self.client.put('/orgs/test-org/actions/secrets/SECRET',
                                   json={'encrypted_value': 'test', 'key_id': '123'},
                                   headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # DELETE /orgs/{org}/actions/secrets/{name} tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete_org_secret__success(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'TO_DELETE', encrypted, key_id)

        response = self.client.delete('/orgs/test-org/actions/secrets/TO_DELETE',
                                      headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 204
        assert self.state.get_org_secret('test-org', 'TO_DELETE') is None

    def test__delete_org_secret__not_found(self):
        self.state.add_org('test-org')

        response = self.client.delete('/orgs/test-org/actions/secrets/NONEXISTENT',
                                      headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__delete_org_secret__org_not_found(self):
        response = self.client.delete('/orgs/nonexistent/actions/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.org_admin_pat()}'})

        assert response.status_code == 404

    def test__delete_org_secret__no_permission(self):
        self.state.add_org('test-org')
        scope_id  = self.keys.scope_id_for_org('test-org')
        encrypted = self.keys.encrypt_secret(scope_id, 'value')
        key_id    = self.keys.get_key_id(scope_id)
        self.state.set_org_secret('test-org', 'SECRET', encrypted, key_id)

        response = self.client.delete('/orgs/test-org/actions/secrets/SECRET',
                                      headers={'Authorization': f'token {self.pats.repo_write_pat()}'})

        assert response.status_code == 403