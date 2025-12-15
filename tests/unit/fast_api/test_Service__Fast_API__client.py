from unittest                                                               import TestCase
from fastapi                                                                import FastAPI
from osbot_fast_api.api.Fast_API                                            import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api.api.schemas.consts.consts__Fast_API                     import EXPECTED_ROUTES__SET_COOKIE
from osbot_fast_api_serverless.fast_api.routes.Routes__Info                 import ROUTES_INFO__HEALTH__RETURN_VALUE, ROUTES_PATHS__INFO
from osbot_utils.utils.Env                                                  import get_env
from starlette.testclient                                                   import TestClient
from mgraph_ai_service_github.fast_api.GitHub__Service__Fast_API            import GitHub__Service__Fast_API
from mgraph_ai_service_github.fast_api.routes.Routes__Auth                  import ROUTES_PATHS__AUTH
from mgraph_ai_service_github.fast_api.routes.Routes__Encryption            import ROUTES_PATHS__ENCRYPTION
from mgraph_ai_service_github.fast_api.routes.Routes__GitHub__Secrets__Env  import ROUTES_PATHS__GITHUB_SECRETS_ENV
from mgraph_ai_service_github.fast_api.routes.Routes__GitHub__Secrets__Org  import ROUTES_PATHS__GITHUB_SECRETS_ORG
from mgraph_ai_service_github.fast_api.routes.Routes__GitHub__Secrets__Repo import ROUTES_PATHS__GITHUB_SECRETS_REPO
from tests.unit.GitHub__Service__Fast_API__Test_Objs                        import setup__github_service_fast_api_test_objs, GitHub__Service__Fast_API__Test_Objs, TEST_API_KEY__NAME


class test_Service__Fast_API__client(TestCase):

    @classmethod
    def setUpClass(cls):
        with setup__github_service_fast_api_test_objs() as _:
            cls.service_fast_api_test_objs         = _
            cls.fast_api                           = cls.service_fast_api_test_objs.fast_api
            cls.client                             = cls.service_fast_api_test_objs.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = ''

    def test__init__(self):
        with self.service_fast_api_test_objs as _:
            assert type(_) is GitHub__Service__Fast_API__Test_Objs
            assert type(_.fast_api        ) is GitHub__Service__Fast_API
            assert type(_.fast_api__app   ) is FastAPI
            assert type(_.fast_api__client) is TestClient
            assert self.fast_api            == _.fast_api
            assert self.client              == _.fast_api__client

    def test__client__auth(self):
        path                = '/info/health'
        auth_key_name       = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME )
        auth_key_value      = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)
        headers             = {auth_key_name: auth_key_value}

        response__no_auth   = self.client.get(url=path, headers={})
        response__with_auth = self.client.get(url=path, headers=headers)

        assert response__no_auth.status_code == 401
        assert response__no_auth.json()      == { 'data'   : None,
                                                  'error'  : None,
                                                  'message': 'Client API key is missing, you need to set it on a header or cookie',
                                                  'status' : 'error'}

        assert auth_key_name                 is not None
        assert auth_key_value                is not None
        assert response__with_auth.json()    == ROUTES_INFO__HEALTH__RETURN_VALUE

    def test__config_fast_api_routes(self):
        assert self.fast_api.routes_paths() == sorted(ROUTES_PATHS__INFO                +
                                                      ROUTES_PATHS__AUTH                +
                                                      ROUTES_PATHS__ENCRYPTION          +
                                                      EXPECTED_ROUTES__SET_COOKIE       +
                                                      ROUTES_PATHS__GITHUB_SECRETS_REPO +
                                                      ROUTES_PATHS__GITHUB_SECRETS_ENV  +
                                                      ROUTES_PATHS__GITHUB_SECRETS_ORG  )