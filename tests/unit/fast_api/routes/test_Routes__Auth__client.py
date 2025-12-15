import pytest
import base64
import re
from unittest                                                               import TestCase
from osbot_fast_api.api.routes.Fast_API__Routes                             import Fast_API__Routes
from osbot_fast_api.api.schemas.Schema__Fast_API__Config                    import Schema__Fast_API__Config
from osbot_utils.testing.__                                                 import __
from osbot_utils.testing.__helpers                                          import obj
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                         import Safe_Str
from osbot_utils.utils.Env                                                  import env_var_set, get_env, load_dotenv
from starlette.testclient                                                   import TestClient
from mgraph_ai_service_github.config                                        import ENV_VAR__SERVICE__AUTH__PUBLIC_KEY, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY
from mgraph_ai_service_github.fast_api.GitHub__Service__Fast_API            import GitHub__Service__Fast_API
from mgraph_ai_service_github.utils.Version                                 import version__mgraph_ai_service_github
from tests.unit.GitHub__Service__Fast_API__Test_Objs                        import setup__github_service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE, GitHub__Service__Fast_API__Test_Objs


class test_Routes__Auth__client(TestCase):

    @classmethod
    def setUpClass(cls):
        with setup__github_service_fast_api_test_objs() as _:
            cls.test_objs      = _
            cls.github_service = _.fast_api
            cls.client         = _.fast_api__client
            cls.nacl_keys      = _.nacl_keys
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Verification Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_setUpClass(self):                                                                  # Verify test setup is correct
        with self.test_objs as _:
            assert type(_) is GitHub__Service__Fast_API__Test_Objs

        with self.github_service as _:
            assert type(_) is GitHub__Service__Fast_API

        with self.client as _:
            assert type(_) is TestClient

        assert env_var_set(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY ) is True
        assert env_var_set(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY) is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /auth/public-key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_public_key(self):                                                            # Test GET /auth/public-key returns public key
        response = self.client.get('/auth/public-key')
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('algorithm')  == 'NaCl/Curve25519/SealedBox'
        assert result.get('timestamp')  is not None

        public_key = result.get('public_key')
        assert public_key                                       is not None                     # Key must be configured
        assert len(public_key)                                  == 64                           # 32 bytes as hex
        assert all(c in '0123456789abcdef' for c in public_key)                                 # Valid lowercase hex
        assert public_key                                       == self.nacl_keys.public_key    # Should match what we set

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /auth/test-api-key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_test_api_key(self):                                                          # Test GET /auth/test-api-key returns service info
        response = self.client.get('/auth/test-api-key')
        result   = response.json()
        assert obj(result)                   == __(success         =  True                            ,
                                                   service         = 'mgraph_ai_service_github'       ,
                                                   version         = version__mgraph_ai_service_github,
                                                   auth_configured = True                             ,
                                                   message         = 'Service API key is valid'       )
        assert response.status_code          == 200
        assert result.get('success'        ) is True
        assert result.get('service'        ) == 'mgraph_ai_service_github'
        assert result.get('version'        ) is not None
        assert result.get('auth_configured') is True                                            # Keys are configured in setUpClass
        assert result.get('message'        )  == 'Service API key is valid'

    # ═══════════════════════════════════════════════════════════════════════════════
    # POST /auth/token-create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_token_create__missing_header(self):                                          # Test POST /auth/token-create without X-GitHub-PAT header
        response = self.client.post('/auth/token-create')
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error')      == 'Missing X-GitHub-PAT header'
        assert result.get('error_type') == 'MISSING_HEADER'

    def test__auth_token_create__empty_header(self):                                            # Test POST /auth/token-create with empty header
        response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': ''})
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error')      == 'Missing X-GitHub-PAT header'
        assert result.get('error_type') == 'MISSING_HEADER'

    def test__auth_token_create__invalid_pat(self):                                             # Test POST /auth/token-create with invalid PAT (real GitHub call)
        response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': 'ghp_invalid_pat_12345'})
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error_type') == 'INVALID_PAT'
        assert 'Bad credentials'        in result.get('error', '')

    # ═══════════════════════════════════════════════════════════════════════════════
    # POST /auth/token-validate Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_token_validate__missing_header(self):                                        # Test POST /auth/token-validate without header
        response = self.client.post('/auth/token-validate')
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error')      == 'Missing X-OSBot-GitHub-PAT header'
        assert result.get('error_type') == 'MISSING_HEADER'

    def test__auth_token_validate__invalid_base64(self):                                        # Test POST /auth/token-validate with invalid base64
        response = self.client.post('/auth/token-validate', headers={'X-OSBot-GitHub-PAT': 'not-valid-base64!!!'})
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error_type') == 'DECRYPTION_FAILED'

    def test__auth_token_validate__invalid_encrypted_data(self):                                # Test POST /auth/token-validate with valid base64 but not NaCl encrypted
        fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')

        response = self.client.post('/auth/token-validate', headers={'X-OSBot-GitHub-PAT': fake_encrypted})
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error_type') == 'DECRYPTION_FAILED'

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /auth/test Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_test__missing_header(self):                                                  # Test GET /auth/test without header
        response = self.client.get('/auth/test')
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error')      == 'Missing X-OSBot-GitHub-PAT header'
        assert result.get('error_type') == 'MISSING_HEADER'

    def test__auth_test__invalid_encrypted_data(self):                                          # Test GET /auth/test with invalid encrypted data
        fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')

        response = self.client.get('/auth/test', headers={'X-OSBot-GitHub-PAT': fake_encrypted})
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is False
        assert result.get('error_type') == 'DECRYPTION_FAILED'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Flow Tests (Encryption Round-Trip)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth__encrypt_decrypt_flow(self):                                                 # Test encrypt -> decrypt -> GitHub validation flow
        test_pat = 'ghp_test_pat_value_12345'
        #Encrypt using the service's public key
        encrypt_response = self.client.post('/encryption/encrypt', json={ 'value'          : test_pat,
                                                                          'encryption_type': 'text'})

        encrypt_result = encrypt_response.json()

        assert encrypt_result.get('success') is True
        encrypted_pat = encrypt_result.get('encrypted')

        # Validate with encrypted value - decryption succeeds but GitHub rejects invalid PAT
        validate_response = self.client.post('/auth/token-validate', headers={'X-OSBot-GitHub-PAT': encrypted_pat})
        validate_result   = validate_response.json()

        assert validate_response.status_code == 200
        assert validate_result.get('success')    is False
        assert validate_result.get('error_type') == 'INVALID_PAT'                               # Decryption worked, GitHub rejected
        assert 'Bad credentials'                 in validate_result.get('error', '')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Authentication Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth__no_api_key(self):                                                           # Test routes require API key authentication
        with setup__github_service_fast_api_test_objs() as _:
            client_no_auth = TestClient(_.fast_api__app)

        response = client_no_auth.get('/auth/public-key')

        assert response.status_code == 401
        result = response.json()
        assert result.get('status')  == 'error'
        assert 'API key'             in result.get('message', '')


class test_Routes__Auth__client__with_github_pat(TestCase):                                     # Tests requiring real GitHub PAT

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.github_pat = get_env('GIT_HUB__ACCESS_TOKEN', '')
        if not cls.github_pat:
            return                                                                              # Skip setup if no PAT

        with setup__github_service_fast_api_test_objs() as _:
            cls.test_objs = _
            cls.client    = _.fast_api__client
            cls.nacl_keys = _.nacl_keys
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def setUp(self):
        if not self.github_pat:
            self.skipTest("GIT_HUB__ACCESS_TOKEN not set")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Flow Tests with Real GitHub PAT
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_token_create__success(self):                                                 # Test POST /auth/token-create with real PAT
        response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
        result   = response.json()

        assert response.status_code        == 200
        assert result.get('success')       is True
        assert result.get('encrypted_pat') is not None
        assert result.get('user')          is not None
        assert result.get('user')['login'] is not None
        assert result.get('user')['id']    is not None
        assert result.get('instructions')  is not None

        self.__class__.encrypted_pat = result.get('encrypted_pat')

    def test__auth_token_validate__success(self):                                               # Test POST /auth/token-validate with real encrypted PAT
        if not hasattr(self.__class__, 'encrypted_pat'):
            create_response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
            create_result   = create_response.json()
            if not create_result.get('success'):
                self.skipTest(f"token-create failed: {create_result.get('error')}")
            self.__class__.encrypted_pat = create_result.get('encrypted_pat')

        response = self.client.post('/auth/token-validate', headers={'X-OSBot-GitHub-PAT': self.encrypted_pat})
        result   = response.json()

        assert response.status_code                  == 200
        assert result.get('success')                 is True
        assert result.get('user')                    is not None
        assert result.get('user')['login']           is not None
        assert result.get('rate_limit')              is not None
        assert result.get('rate_limit')['limit']     is not None
        assert result.get('rate_limit')['remaining'] is not None

    def test__auth_test__success(self):                                                         # Test GET /auth/test with real encrypted PAT
        if not hasattr(self.__class__, 'encrypted_pat'):
            create_response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
            create_result   = create_response.json()
            if not create_result.get('success'):
                self.skipTest(f"token-create failed: {create_result.get('error')}")
            self.__class__.encrypted_pat = create_result.get('encrypted_pat')

        response = self.client.get('/auth/test', headers={'X-OSBot-GitHub-PAT': self.encrypted_pat})
        result   = response.json()

        assert response.status_code              == 200
        assert result.get('success')             is True
        assert result.get('user')['login']       is not None
        assert result.get('rate_limit')['limit'] is not None

    def test__regression__fast_api__response__base_model__not_handing__none_values__in_type_safe_primitives(self):
        from osbot_fast_api.api.Fast_API import Fast_API

        class An_Response_Class(Type_Safe):
            an_str : Safe_Str = None

        class Routes__ABC(Fast_API__Routes):
            def an_post__fails(self) -> An_Response_Class:
                return An_Response_Class()

            def an_post__ok_1(self) -> An_Response_Class:
                return An_Response_Class(an_str='')

            def an_post__ok_2(self) -> An_Response_Class:
                return An_Response_Class(an_str='ok')

            def setup_routes(self):
                self.add_routes_post(self.an_post__fails,
                                     self.an_post__ok_1 ,
                                     self.an_post__ok_2 )

        config  = Schema__Fast_API__Config(default_routes=False)
        class Fast_API__Abc(Fast_API):
            def setup_routes(self):
                self.add_routes(Routes__ABC)
                return self

        fast_api_abc = Fast_API__Abc(config=config).setup()
        assert fast_api_abc.routes_paths() == ['/an-post/fails',
                                               '/an-post/ok-1',
                                               '/an-post/ok-2']

        with fast_api_abc.client() as _:
            #error_message = "1 validation error for An_Response_Class__BaseModel\nan_str\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.12/v/string_type"
            # with pytest.raises(ValueError, match=re.escape(error_message)):
            #     _.post(url='/an-post/fails')                                # BUG: should have worked
            assert _.post(url='/an-post/fails').json() == {'an_str': None}    # FIXED

            assert _.post(url='/an-post/ok-1').json() == {'an_str': ''  }
            assert _.post(url='/an-post/ok-2').json() == {'an_str': 'ok'}
