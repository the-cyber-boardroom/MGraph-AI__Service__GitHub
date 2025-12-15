from unittest                                                                       import TestCase
from unittest.mock                                                                  import patch
from osbot_fast_api.api.routes.Fast_API__Routes                                     import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_github.fast_api.routes.Routes__Auth                          import Routes__Auth, TAG__ROUTES_AUTH, ROUTES_PATHS__AUTH
from mgraph_ai_service_github.schemas.encryption.Schema__Public_Key__Response       import Schema__Public_Key__Response
from mgraph_ai_service_github.service.auth.Service__Auth                            import Service__Auth
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management               import NaCl__Key_Management


class test_Routes__Auth(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nacl_manager = NaCl__Key_Management()
        cls.test_keys    = cls.nacl_manager.generate_nacl_keys()
        cls.service_auth = Service__Auth(private_key_hex = cls.test_keys.private_key ,
                                         public_key_hex  = cls.test_keys.public_key  )
        cls.routes_auth  = Routes__Auth(service_auth = cls.service_auth)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                     # Test auto-initialization
        with self.routes_auth as _:
            assert type(_)              is Routes__Auth
            assert base_classes(_)      == [Fast_API__Routes, Type_Safe, object]
            assert _.tag                == TAG__ROUTES_AUTH
            assert type(_.service_auth) is Service__Auth

    def test__routes_paths(self):                                                               # Test route paths constant
        assert ROUTES_PATHS__AUTH == [ '/auth/public-key'     ,
                                       '/auth/token-create'   ,
                                       '/auth/token-validate' ,
                                       '/auth/test'           ,
                                       '/auth/test-api-key'   ]
        assert len(ROUTES_PATHS__AUTH) == 5

    # ═══════════════════════════════════════════════════════════════════════════════
    # public_key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__public_key(self):                                                                 # Test public_key returns correct response
        with self.routes_auth as _:
            result = _.public_key()

            assert type(result)            is Schema__Public_Key__Response
            assert result.public_key       == self.test_keys.public_key
            assert result.algorithm        == 'NaCl/Curve25519/SealedBox'
            assert result.timestamp        is not None

    def test__public_key__key_format(self):                                                     # Test public key is valid hex format
        with self.routes_auth as _:
            result     = _.public_key()
            public_key = result.public_key

            assert len(public_key)                              == 64                           # 32 bytes as hex
            assert all(c in '0123456789abcdef' for c in public_key)                             # Valid lowercase hex

    # ═══════════════════════════════════════════════════════════════════════════════
    # token_create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__token_create__missing_header(self):                                               # Test token_create without PAT header
        with self.routes_auth as _:
            result = _.token_create(github_pat=None)

            assert result['success']    is False
            assert result['error']      == 'Missing X-GitHub-PAT header'
            assert result['error_type'] == 'MISSING_HEADER'

    def test__token_create__empty_header(self):                                                 # Test token_create with empty PAT
        with self.routes_auth as _:
            result = _.token_create(github_pat='')

            assert result['success']    is False
            assert result['error']      == 'Missing X-GitHub-PAT header'
            assert result['error_type'] == 'MISSING_HEADER'

    @patch.object(Service__Auth, 'test_github_pat')
    @patch.object(Service__Auth, 'encrypt_pat')
    def test__token_create__success(self, mock_encrypt, mock_test):                             # Test token_create with valid PAT
        mock_test.return_value    = { 'success' : True                              ,
                                      'user'    : { 'login' : 'testuser', 'id': 123}}
        mock_encrypt.return_value = 'encrypted_pat_value_base64'

        with self.routes_auth as _:
            result = _.token_create(github_pat='ghp_valid_test_pat')

            assert result['success']       is True
            assert result['encrypted_pat'] == 'encrypted_pat_value_base64'
            assert result['user']          == {'login': 'testuser', 'id': 123}
            assert result['instructions']  is not None

    @patch.object(Service__Auth, 'test_github_pat')
    def test__token_create__invalid_pat(self, mock_test):                                       # Test token_create with invalid PAT
        mock_test.return_value = { 'success'    : False                 ,
                                   'error'      : 'Bad credentials'     ,
                                   'error_type' : 'INVALID_PAT'         }

        with self.routes_auth as _:
            result = _.token_create(github_pat='ghp_invalid_pat')

            assert result['success']    is False
            assert result['error']      == 'Bad credentials'
            assert result['error_type'] == 'INVALID_PAT'

    @patch.object(Service__Auth, 'test_github_pat')
    @patch.object(Service__Auth, 'encrypt_pat')
    def test__token_create__encryption_failed(self, mock_encrypt, mock_test):                   # Test token_create when encryption fails
        mock_test.return_value = { 'success' : True                              ,
                                   'user'    : { 'login' : 'testuser', 'id': 123}}
        mock_encrypt.side_effect = Exception('Encryption error')

        with self.routes_auth as _:
            result = _.token_create(github_pat='ghp_valid_pat')

            assert result['success']    is False
            assert 'Encryption error'   in result['error']
            assert result['error_type'] == 'ENCRYPTION_FAILED'

    # ═══════════════════════════════════════════════════════════════════════════════
    # token_validate Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__token_validate__missing_header(self):                                             # Test token_validate without encrypted PAT
        with self.routes_auth as _:
            result = _.token_validate(x_osbot_github_pat=None)

            assert result['success']    is False
            assert result['error']      == 'Missing X-OSBot-GitHub-PAT header'
            assert result['error_type'] == 'MISSING_HEADER'

    @patch.object(Service__Auth, 'test')
    def test__token_validate__success(self, mock_test):                                         # Test token_validate with valid encrypted PAT
        mock_test.return_value = { 'success'    : True                                  ,
                                   'user'       : { 'login' : 'testuser', 'id': 123}    ,
                                   'rate_limit' : { 'limit' : 5000, 'remaining': 4999}  }

        with self.routes_auth as _:
            result = _.token_validate(x_osbot_github_pat='valid_encrypted_pat')

            assert result['success']    is True
            assert result['user']       is not None
            assert result['rate_limit'] is not None
            mock_test.assert_called_once_with(encrypted_pat='valid_encrypted_pat')

    @patch.object(Service__Auth, 'test')
    def test__token_validate__decryption_failed(self, mock_test):                               # Test token_validate with invalid encrypted data
        mock_test.return_value = { 'success'    : False                         ,
                                   'error'      : 'Decryption failed'           ,
                                   'error_type' : 'DECRYPTION_FAILED'           }

        with self.routes_auth as _:
            result = _.token_validate(x_osbot_github_pat='invalid_encrypted_data')

            assert result['success']    is False
            assert result['error_type'] == 'DECRYPTION_FAILED'

    # ═══════════════════════════════════════════════════════════════════════════════
    # test Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__test__missing_header(self):                                                       # Test /auth/test without encrypted PAT
        with self.routes_auth as _:
            result = _.test(x_osbot_github_pat=None)

            assert result['success']    is False
            assert result['error']      == 'Missing X-OSBot-GitHub-PAT header'
            assert result['error_type'] == 'MISSING_HEADER'

    @patch.object(Service__Auth, 'test')
    def test__test__success(self, mock_test):                                                   # Test /auth/test with valid encrypted PAT
        mock_test.return_value = { 'success'    : True                                          ,
                                   'user'       : { 'login'       : 'testuser'                  ,
                                                   'id'          : 123                          ,
                                                   'public_repos': 42                           },
                                   'rate_limit' : { 'limit'     : 5000                          ,
                                                   'remaining' : 4999                           ,
                                                   'used'      : 1                              }}

        with self.routes_auth as _:
            result = _.test(x_osbot_github_pat='valid_encrypted_pat')

            assert result['success']               is True
            assert result['user']['login']         == 'testuser'
            assert result['user']['public_repos']  == 42
            assert result['rate_limit']['limit']   == 5000
            mock_test.assert_called_once_with(encrypted_pat='valid_encrypted_pat')

    # ═══════════════════════════════════════════════════════════════════════════════
    # test_api_key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__test_api_key(self):                                                               # Test /auth/test-api-key returns service info
        with self.routes_auth as _:
            result = _.test_api_key()

            assert result['success']         is True
            assert result['service']         == 'mgraph_ai_service_github'
            assert result['version']         is not None
            assert result['auth_configured'] is True                                            # Keys are configured in setUpClass
            assert result['message']         == 'Service API key is valid'

    # def test__test_api_key__no_keys_configured(self):                                           # Test test_api_key when keys not configured
    #     routes_auth = Routes__Auth(service_auth = Service__Auth(private_key_hex = '' ,
    #                                                             public_key_hex  = '' ))
    #     with routes_auth as _:
    #         result = _.test_api_key()
    #
    #         assert result['success']         is True
    #         assert result['auth_configured'] is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                               # Test setup_routes returns self
        routes = Routes__Auth(service_auth = self.service_auth)
        result = routes.setup_routes()

        assert result is None                                                                   # setup_routes doesn't return self in this implementation