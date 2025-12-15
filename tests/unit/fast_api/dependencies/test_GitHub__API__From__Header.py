import pytest
from unittest                                                                   import TestCase
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from osbot_utils.utils.Env                                                      import get_env, load_dotenv
from osbot_utils.utils.Objects                                                  import base_classes
from mgraph_ai_service_github.config                                            import ENV_VAR__GIT_HUB__ACCESS_TOKEN
from mgraph_ai_service_github.fast_api.dependencies.GitHub__API__From__Header   import GitHub__API__From__Header
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type          import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Request    import Schema__Encryption__Request
from mgraph_ai_service_github.service.auth.Service__Auth                        import Service__Auth
from mgraph_ai_service_github.service.encryption.Service__Encryption            import Service__Encryption
from mgraph_ai_service_github.service.github.GitHub__API                        import GitHub__API
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management           import NaCl__Key_Management


class test_GitHub__API__From__Header(TestCase):

    @classmethod
    def setUpClass(cls):                                                                        # Setup test configuration
        cls.nacl_manager       = NaCl__Key_Management()
        cls.test_keys          = cls.nacl_manager.generate_nacl_keys()
        cls.service_auth       = Service__Auth      (private_key_hex = cls.test_keys.private_key ,
                                                     public_key_hex  = cls.test_keys.public_key  )
        cls.service_encryption = Service__Encryption(private_key_hex = cls.test_keys.private_key ,
                                                     public_key_hex  = cls.test_keys.public_key  )
        cls.api_factory        = GitHub__API__From__Header(service_auth = cls.service_auth)

        load_dotenv()
        cls.github_pat = get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN)
        if not cls.github_pat:
            pytest.skip('Skipping tests because GitHub Access Token is not available')

        cls.encrypt_request = Schema__Encryption__Request(value           = cls.github_pat            ,
                                                          encryption_type = Enum__Encryption_Type.TEXT)
        cls.encrypted_pat   = cls.service_encryption.encrypt(cls.encrypt_request).encrypted

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                     # Test auto-initialization
        with self.api_factory as _:
            assert type(_)              is GitHub__API__From__Header
            assert base_classes(_)      == [Type_Safe, object]
            assert type(_.service_auth) is Service__Auth

    # ═══════════════════════════════════════════════════════════════════════════════
    # get_api Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get_api__success(self):                                                           # Test get_api returns configured GitHub__API
        with self.api_factory as _:
            result = _.get_api(self.encrypted_pat)

            assert type(result)      is GitHub__API
            assert result.api_token  == self.github_pat                                         # Decrypted token matches original
            assert result.api_url    == 'https://api.github.com'

    def test__get_api__can_make_api_calls(self):                                                # Test returned GitHub__API can actually make calls
        with self.api_factory as _:
            github_api = _.get_api(self.encrypted_pat)
            user_info  = github_api.get('/user')                                                # Make real API call

            assert type(user_info)  is dict
            assert 'login'          in user_info
            assert 'id'             in user_info

    def test__get_api__decryption_round_trip(self):                                             # Test encrypt -> decrypt preserves PAT
        test_pat        = 'ghp_test_token_abc123'
        encrypt_request = Schema__Encryption__Request(value           = test_pat                    ,
                                                      encryption_type = Enum__Encryption_Type.TEXT  )
        encrypted       = self.service_encryption.encrypt(encrypt_request).encrypted

        with self.api_factory as _:
            github_api = _.get_api(encrypted)

            assert github_api.api_token == test_pat                                             # Token should match original

    def test__get_api__invalid_encrypted_data(self):                                            # Test get_api with invalid encrypted data
        with self.api_factory as _:
            with self.assertRaises(Exception) as context:
                _.get_api('not_valid_encrypted_data_xyz')

            error_str = str(context.exception).lower()
            assert 'decrypt' in error_str or 'invalid' in error_str or 'base64' in error_str

    def test__get_api__corrupted_encrypted_data(self):                                          # Test get_api with corrupted base64 data
        import base64
        corrupted_data = base64.b64encode(b'x' * 100).decode('utf-8')                           # Valid base64 but not NaCl encrypted

        with self.api_factory as _:
            with self.assertRaises(Exception) as context:
                _.get_api(corrupted_data)

            error_str = str(context.exception).lower()
            assert 'decrypt' in error_str or 'failed' in error_str

    def test__get_api__empty_encrypted_pat(self):                                               # Test get_api with empty string
        with self.api_factory as _:
            with self.assertRaises(Exception):
                _.get_api('')

    def test__get_api__reusable(self):                                                          # Test that factory can create multiple instances
        with self.api_factory as _:
            api1 = _.get_api(self.encrypted_pat)
            api2 = _.get_api(self.encrypted_pat)

            assert api1.api_token == api2.api_token
            assert api1 is not api2                                                             # Different instances