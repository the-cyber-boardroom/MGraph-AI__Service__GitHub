import unittest
from unittest                                                                              import TestCase
from fastapi                                                                               import FastAPI
from fastapi.responses                                                                     import JSONResponse
from osbot_fast_api.api.routes.Fast_API__Routes                                            import Fast_API__Routes
from mgraph_ai_service_github.surrogates.github.routes.Routes__GitHub__Base                import Routes__GitHub__Base
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State              import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs               import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys               import GitHub__API__Surrogate__Keys


class test__Routes__GitHub__Base(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.state  = GitHub__API__Surrogate__State()
        cls.pats   = GitHub__API__Surrogate__PATs().setup()
        cls.keys   = GitHub__API__Surrogate__Keys().setup()
        cls.app    = FastAPI()
        cls.routes = Routes__GitHub__Base(app   = cls.app   ,
                                          state = cls.state ,
                                          pats  = cls.pats  ,
                                          keys  = cls.keys  )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):
        with self.routes as _:
            assert type(_)       is Routes__GitHub__Base
            assert isinstance(_, Fast_API__Routes)
            assert _.state       is self.state
            assert _.pats        is self.pats
            assert _.keys        is self.keys
            assert _.tag         is None                                        # Base class has no tag

    # ═══════════════════════════════════════════════════════════════════════════════
    # extract_pat tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__extract_pat__with_token_prefix(self):
        pat = self.routes.extract_pat('token ghp_test123')
        assert pat == 'ghp_test123'

    def test__extract_pat__with_bearer_prefix(self):
        pat = self.routes.extract_pat('Bearer ghp_test456')
        assert pat == 'ghp_test456'

    def test__extract_pat__without_prefix(self):
        pat = self.routes.extract_pat('ghp_test789')
        assert pat == 'ghp_test789'

    def test__extract_pat__with_none(self):
        pat = self.routes.extract_pat(None)
        assert pat is None

    def test__extract_pat__with_empty_string(self):
        pat = self.routes.extract_pat('')
        assert pat is None                                                      # Empty string treated as no auth

    # ═══════════════════════════════════════════════════════════════════════════════
    # validate_auth tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__validate_auth__valid_admin_pat(self):
        auth = f'token {self.pats.admin_pat()}'
        valid, status, error, pat = self.routes.validate_auth(auth)

        assert valid  is True
        assert status == 200
        assert error  is None
        assert pat    == self.pats.admin_pat()

    def test__validate_auth__no_authorization(self):
        valid, status, error, pat = self.routes.validate_auth(None)

        assert valid  is False
        assert status == 401
        assert error  == {'message': 'Requires authentication', 'documentation_url': 'https://docs.github.com/rest'}
        assert pat    is None

    def test__validate_auth__unknown_pat(self):
        valid, status, error, pat = self.routes.validate_auth('token unknown_pat')

        assert valid  is False
        assert status == 401
        assert error['message'] == 'Bad credentials'
        assert pat    is None

    def test__validate_auth__invalid_pat(self):
        auth = f'token {self.pats.invalid_pat()}'
        valid, status, error, pat = self.routes.validate_auth(auth)

        assert valid  is False
        assert status == 401
        assert error['message'] == 'Bad credentials'

    def test__validate_auth__expired_pat(self):
        auth = f'token {self.pats.expired_pat()}'
        valid, status, error, pat = self.routes.validate_auth(auth)

        assert valid  is False
        assert status == 401
        assert error['message'] == 'Bad credentials'

    def test__validate_auth__rate_limited_pat(self):
        auth = f'token {self.pats.rate_limited_pat()}'
        valid, status, error, pat = self.routes.validate_auth(auth)

        assert valid  is False
        assert status == 429
        assert 'rate limit' in error['message']

    # ═══════════════════════════════════════════════════════════════════════════════
    # Permission check tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__check_repo_read__admin_pat(self):
        can_read, status, error = self.routes.check_repo_read(self.pats.admin_pat())
        assert can_read is True
        assert status   == 200
        assert error    is None

    def test__check_repo_read__repo_read_pat(self):
        can_read, status, error = self.routes.check_repo_read(self.pats.repo_read_pat())
        assert can_read is True

    def test__check_repo_read__no_scopes_pat(self):
        can_read, status, error = self.routes.check_repo_read(self.pats.no_scopes_pat())
        assert can_read is False
        assert status   == 403
        assert error['message'] == 'Resource not accessible by integration'

    def test__check_repo_write__admin_pat(self):
        can_write, status, error = self.routes.check_repo_write(self.pats.admin_pat())
        assert can_write is True

    def test__check_repo_write__repo_read_pat(self):
        can_write, status, error = self.routes.check_repo_write(self.pats.repo_read_pat())
        assert can_write is False
        assert status    == 403

    def test__check_repo_write__repo_write_pat(self):
        can_write, status, error = self.routes.check_repo_write(self.pats.repo_write_pat())
        assert can_write is True

    def test__check_org_admin__org_admin_pat(self):
        can_admin, status, error = self.routes.check_org_admin(self.pats.org_admin_pat())
        assert can_admin is True

    def test__check_org_admin__repo_write_pat(self):
        can_admin, status, error = self.routes.check_org_admin(self.pats.repo_write_pat())
        assert can_admin is False
        assert status    == 403

    # ═══════════════════════════════════════════════════════════════════════════════
    # Error response helper tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test___error_response(self):
        error = self.routes._error_response("Test error", 400)
        assert error == {'message': 'Test error', 'documentation_url': 'https://docs.github.com/rest'}

    def test___rate_limit_error(self):
        error = self.routes._rate_limit_error()
        assert 'rate limit' in error['message']
        assert 'documentation_url' in error

    def test__not_found_response(self):
        response = self.routes.not_found_response()
        assert type(response) is JSONResponse
        assert response.status_code == 404

    # ═══════════════════════════════════════════════════════════════════════════════
    # Auth error response helper tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_error_response__valid(self):
        auth = f'token {self.pats.admin_pat()}'
        valid, response, pat = self.routes.auth_error_response(auth)

        assert valid    is True
        assert response is None
        assert pat      == self.pats.admin_pat()

    def test__auth_error_response__invalid(self):
        valid, response, pat = self.routes.auth_error_response(None)

        assert valid    is False
        assert type(response) is JSONResponse
        assert response.status_code == 401
        assert pat      is None

    def test__repo_read_error_response__allowed(self):
        allowed, response = self.routes.repo_read_error_response(self.pats.admin_pat())
        assert allowed  is True
        assert response is None

    def test__repo_read_error_response__denied(self):
        allowed, response = self.routes.repo_read_error_response(self.pats.no_scopes_pat())
        assert allowed  is False
        assert type(response) is JSONResponse
        assert response.status_code == 403

    def test__repo_write_error_response__allowed(self):
        allowed, response = self.routes.repo_write_error_response(self.pats.admin_pat())
        assert allowed  is True
        assert response is None

    def test__repo_write_error_response__denied(self):
        allowed, response = self.routes.repo_write_error_response(self.pats.repo_read_pat())
        assert allowed  is False
        assert response.status_code == 403

    def test__org_admin_error_response__allowed(self):
        allowed, response = self.routes.org_admin_error_response(self.pats.org_admin_pat())
        assert allowed  is True
        assert response is None

    def test__org_admin_error_response__denied(self):
        allowed, response = self.routes.org_admin_error_response(self.pats.repo_write_pat())
        assert allowed  is False
        assert response.status_code == 403