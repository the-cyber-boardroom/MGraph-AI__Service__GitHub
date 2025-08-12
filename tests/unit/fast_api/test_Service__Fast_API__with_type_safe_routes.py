from unittest                                                                   import TestCase
from osbot_fast_api.api.Fast_API                                                import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_fast_api.api.Fast_API_Routes                                         import Fast_API_Routes
from osbot_utils.helpers.Timestamp_Now                                          import Timestamp_Now
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Env                                                      import get_env, load_dotenv
from osbot_utils.utils.Misc                                                     import random_text
from mgraph_ai_service_github.fast_api.Service__Fast_API                        import Service__Fast_API
from mgraph_ai_service_github.fast_api.routes.Routes__Auth                      import ROUTES_PATHS__AUTH
from mgraph_ai_service_github.fast_api.routes.Routes__Encryption import ROUTES_PATHS__ENCRYPTION
from mgraph_ai_service_github.fast_api.routes.Routes__Info                      import ROUTES_PATHS__INFO
from mgraph_ai_service_github.schemas.encryption.Const__Encryption              import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Schema__Public_Key__Response   import Schema__Public_Key__Response

class test_Service__Fast_API__with_type_safe_routes(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.auth_key_name    = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME)      # todo: add this to Service__Fast_API__Test_Objs
        cls.auth_key_value   = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE)
        cls.headers          = { cls.auth_key_name: cls.auth_key_value}
        cls.routes_paths     = sorted(ROUTES_PATHS__INFO       +
                                      ROUTES_PATHS__AUTH       +
                                      ROUTES_PATHS__ENCRYPTION +
                                      ['/type_safe/ping']      )

    def setUp(self):
        self.service_fast_api = Service__Fast_API().setup()  # we need fresh copies of this Fast_API service for the tests below (since they are adding routes)

    def test_setUpClass(self):
        with self.service_fast_api as _:
            assert type(_) is Service__Fast_API

    def test__add_type_safe_routes__simple_example(self):
        class An_Class(Type_Safe):
            an_str : str

        class Type_Safe__Routes(Fast_API_Routes):
            tag = 'type_safe'

            def ping(self, an_class: An_Class):
                return {'pong': an_class}

            def setup_routes(self):
                self.add_route_post(self.ping)
        with self.service_fast_api as _:
            _.add_routes(Type_Safe__Routes)
            assert _.routes_paths() == self.routes_paths

            an_str    = random_text()
            post_data = An_Class(an_str=an_str).json()
            response = _.client().post('/type_safe/ping', headers=self.headers, json=post_data)
            assert response.status_code == 200
            assert response.json()      == {'pong': {'an_str': an_str}}


    def test__regression__fast_api_error_on__Schema__Public_Key__Response(self):
        class An_Class(Type_Safe):
            public_key_response : Schema__Public_Key__Response

        class Type_Safe__Routes(Fast_API_Routes):
            tag = 'type_safe'

            def ping(self, an_class: An_Class) -> An_Class:
                return {'pong': an_class}

            def setup_routes(self):
                self.add_route_post(self.ping)
        with self.service_fast_api as _:
            _.add_routes(Type_Safe__Routes)
            assert _.routes_paths() == self.routes_paths

            public_key          = 'a'*64
            timestamp           = Timestamp_Now()
            public_key_response = Schema__Public_Key__Response(public_key=public_key, timestamp=timestamp)
            post_data           = An_Class(public_key_response=public_key_response).json()
            response            = _.client().post('/type_safe/ping', headers=self.headers, json=post_data)
            assert response.status_code == 200
            assert response.json()      == {'pong': {'public_key_response': {'public_key': public_key      ,
                                                                             'algorithm' : NCCL__ALGORITHM ,
                                                                             'timestamp' : timestamp       }}}