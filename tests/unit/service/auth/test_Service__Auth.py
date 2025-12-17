import base64
from unittest                                                               import TestCase
from nacl.public                                                            import PrivateKey, PublicKey, SealedBox
from osbot_utils.testing.Temp_Env_Vars                                      import Temp_Env_Vars
from osbot_utils.utils.Env                                                  import get_env, load_dotenv, env_var_set
from mgraph_ai_service_github.config                                        import ENV_VAR__SERVICE__AUTH__PUBLIC_KEY, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY
from mgraph_ai_service_github.service.auth.Service__Auth                    import Service__Auth
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management       import NaCl__Key_Management
from mgraph_ai_service_github.surrogates.github.testing.GitHub__API__Surrogate__Test_Context import GitHub__API__Surrogate__Test_Context
from tests.unit.GitHub__Service__Fast_API__Test_Objs                        import create_and_set_nacl_keys


class test_Service__Auth(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nacl_manager = NaCl__Key_Management()
        cls.nacl_keys    = create_and_set_nacl_keys()                                           # Use shared key setup
        cls.auth_service = Service__Auth()
        cls.test_pat           = "ghp_testtoken123456789"
        cls.encrypted_test_pat = cls._encrypt_pat(cls.test_pat, cls.nacl_keys.public_key)

        cls.surrogate_context = GitHub__API__Surrogate__Test_Context().setup()

    @classmethod
    def tearDownClass(cls):
        cls.surrogate_context.teardown()

    @classmethod
    def _encrypt_pat(cls, pat            : str ,                                                # PAT to encrypt
                          public_key_hex : str                                                  # Public key in hex format
                     ) -> str:                                                                  # Returns base64 encoded encrypted PAT
        public_key = PublicKey(bytes.fromhex(public_key_hex))
        sealed_box = SealedBox(public_key)
        encrypted  = sealed_box.encrypt(pat.encode('utf-8'))

        return base64.b64encode(encrypted).decode('utf-8')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Verification Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_setUpClass(self):                                                                  # Verify test setup is correct
        assert env_var_set(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY ) is True
        assert env_var_set(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY) is True

        with self.auth_service as _:
            assert type(_) is Service__Auth

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                     # Test initialization with provided keys
        with self.auth_service as _:
            assert type(_)           is Service__Auth
            assert _.private_key_hex == self.nacl_keys.private_key
            assert _.public_key_hex  == self.nacl_keys.public_key
            assert _.private_key_hex is not None
            assert _.public_key_hex  is not None
            assert _.public_key_hex  == get_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY )
            assert _.private_key_hex == get_env(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY)

    def test__init__from_env(self):                                                             # Test initialization from environment variables
        auth_service = Service__Auth()
        assert auth_service.private_key_hex == self.nacl_keys.private_key
        assert auth_service.public_key_hex  == self.nacl_keys.public_key

    # ═══════════════════════════════════════════════════════════════════════════════
    # Public Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_public_key(self):                                                                  # Test public_key returns configured key
        with self.auth_service as _:
            public_key = _.public_key()

            assert public_key      == self.nacl_keys.public_key
            assert len(public_key) == 64

    def test_public_key__missing(self):                                                         # Test public_key raises when not configured
        env_vars = { ENV_VAR__SERVICE__AUTH__PUBLIC_KEY:'' }
        with Temp_Env_Vars(env_vars=env_vars) as _:
            auth_service = Service__Auth(private_key_hex = "a" * 64 ,
                                         public_key_hex  = ""       )
            assert get_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY) == ''
            with self.assertRaises(ValueError) as context:
                auth_service.public_key()

            assert "Public key not configured" in str(context.exception)
        assert get_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY) != ''

    # ═══════════════════════════════════════════════════════════════════════════════
    # Private Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_private_key(self):                                                                 # Test private_key returns PrivateKey object
        with self.auth_service as _:
            private_key = _.private_key()

            assert type(private_key) is PrivateKey

    def test_private_key__missing(self):                                                        # Test private_key raises when not configured
        env_vars = { ENV_VAR__SERVICE__AUTH__PRIVATE_KEY:'' }
        with Temp_Env_Vars(env_vars=env_vars) as _:
            auth_service = Service__Auth(private_key_hex = ""       ,
                                         public_key_hex  = "a" * 64 )

            with self.assertRaises(ValueError) as context:
                auth_service.private_key()

            assert "Private key not configured" in str(context.exception)

        assert "Private key not configured" in str(context.exception)

    def test_private_key__invalid(self):                                                        # Test private_key raises for invalid hex
        auth_service = Service__Auth(private_key_hex = "invalid-hex" ,
                                     public_key_hex  = "a" * 64      )

        with self.assertRaises(ValueError) as context:
            auth_service.private_key()

        assert "Failed to load private key" in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Encrypt PAT Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_encrypt_pat(self):                                                                 # Test PAT encryption
        with self.auth_service as _:
            encrypted = _.encrypt_pat(self.test_pat)

            assert encrypted is not None
            assert len(encrypted) > 0

            decoded = base64.b64decode(encrypted)                                               # Should be valid base64
            assert len(decoded) > len(self.test_pat)                                            # Has NaCl overhead

    def test_encrypt_pat__round_trip(self):                                                     # Test encrypt then decrypt returns original
        with self.auth_service as _:
            encrypted = _.encrypt_pat(self.test_pat)
            decrypted = _.decrypt_pat(encrypted)

            assert decrypted == self.test_pat

    def test_encrypt_pat__unique_each_time(self):                                               # Test encryption produces unique output (NaCl uses random nonce)
        with self.auth_service as _:
            encrypted_1 = _.encrypt_pat(self.test_pat)
            encrypted_2 = _.encrypt_pat(self.test_pat)

            assert encrypted_1 != encrypted_2                                                   # Same input, different output due to random nonce

    # ═══════════════════════════════════════════════════════════════════════════════
    # Decrypt PAT Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_decrypt_pat(self):                                                                 # Test PAT decryption
        with self.auth_service as _:
            decrypted = _.decrypt_pat(self.encrypted_test_pat)

            assert decrypted == self.test_pat

    def test_decrypt_pat__unicode(self):                                                        # Test decrypt with unicode content
        unicode_pat = "ghp_test_世界_🔐"

        with self.auth_service as _:
            encrypted = _.encrypt_pat(unicode_pat)
            decrypted = _.decrypt_pat(encrypted)

            assert decrypted == unicode_pat

    def test_decrypt_pat__invalid_base64(self):                                                 # Test decrypt raises for invalid base64
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat("not-valid-base64!@#$")

            assert "Invalid base64 encoding" in str(context.exception)

    def test_decrypt_pat__invalid_encryption(self):                                             # Test decrypt raises for non-encrypted data
        with self.auth_service as _:
            invalid_encrypted = base64.b64encode(b"not encrypted data").decode('utf-8')

            with self.assertRaises(ValueError) as context:
                _.decrypt_pat(invalid_encrypted)

            assert "Decryption failed" in str(context.exception)

    def test_decrypt_pat__missing(self):                                                        # Test decrypt raises for empty input
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat("")

            assert "Missing encrypted PAT" in str(context.exception)

    def test_decrypt_pat__none(self):                                                           # Test decrypt raises for None input
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat(None)

            assert "Missing encrypted PAT" in str(context.exception)

    def test_decrypt_pat__wrong_key(self):                                                      # Test decrypt fails with wrong key pair
        other_keys           = self.nacl_manager.generate_nacl_keys()
        encrypted_with_other = self._encrypt_pat(self.test_pat, other_keys.public_key)

        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat(encrypted_with_other)

            assert "Decryption failed" in str(context.exception)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test Method - Missing Header Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__missing_header(self):                                                        # Test test() with None encrypted PAT
        with self.auth_service as _:
            result = _.test(None)

            assert result["success"]    is False
            assert result["error"]      == "Missing X-OSBot-GitHub-PAT header"
            assert result["error_type"] == "MISSING_HEADER"
            assert result["user"]       is None
            assert result["rate_limit"] is None

    def test_test__empty_header(self):                                                          # Test test() with empty encrypted PAT
        with self.auth_service as _:
            result = _.test("")

            assert result["success"]    is False
            assert result["error"]      == "Missing X-OSBot-GitHub-PAT header"
            assert result["error_type"] == "MISSING_HEADER"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test Method - Decryption Failure Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__decryption_failed__invalid_base64(self):                                     # Test test() with invalid base64
        with self.auth_service as _:
            result = _.test("invalid-encrypted-data!!!")

            assert result["success"   ] is False
            assert result["error"     ] == "Decryption failed: Invalid encrypted format or wrong key"
            assert result["error_type"] == "DECRYPTION_FAILED"
            assert result["user"      ] is None

    def test_test__decryption_failed__not_encrypted(self):                                      # Test test() with valid base64 but not encrypted
        fake_encrypted = base64.b64encode(b"x" * 100).decode('utf-8')

        with self.auth_service as _:
            result = _.test(fake_encrypted)

            assert result["success"]    is False
            assert result["error_type"] == "DECRYPTION_FAILED"
            assert result["user"]       is None

    def test_test__decryption_failed__wrong_key(self):                                          # Test test() with data encrypted with different key
        other_keys           = self.nacl_manager.generate_nacl_keys()
        encrypted_with_other = self._encrypt_pat(self.test_pat, other_keys.public_key)

        with self.auth_service as _:
            result = _.test(encrypted_with_other)

            assert result["success"]    is False
            assert result["error_type"] == "DECRYPTION_FAILED"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test Method - Invalid PAT Tests (Real GitHub Calls)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__invalid_pat(self):                                                           # Test test() with fake PAT that GitHub rejects
        fake_pat       = "ghp_fake_invalid_pat_12345"
        encrypted_fake = self._encrypt_pat(fake_pat, self.nacl_keys.public_key)

        with self.auth_service as _:
            result = _.test(encrypted_fake)

            assert result["success"]     is False
            assert result["error_type"]  == "INVALID_PAT"
            assert "Bad credentials"     in result["error"]
            assert result["user"]        is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test GitHub PAT Tests (Real GitHub Calls)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test_github_pat__invalid(self):                                                    # Test test_github_pat() with invalid PAT
        with self.auth_service as _:
            result = _.test_github_pat("ghp_invalid_pat_12345")

            assert result["success"]    is False
            assert result["error_type"] == "INVALID_PAT"
            assert "Bad credentials"    in result["error"]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test API Key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test_api_key(self):                                                                # Test test_api_key() returns service info
        with self.auth_service as _:
            result = _.test_api_key()

            assert result["success"]         is True
            assert result["service"]         == "mgraph_ai_service_github"
            assert result["version"]         is not None
            assert result["auth_configured"] is True
            assert result["message"]         == "Service API key is valid"

    def test_test_api_key__no_keys_configured(self):                                            # Test test_api_key() when keys not configured
        env_vars = { ENV_VAR__SERVICE__AUTH__PUBLIC_KEY:'' }
        with Temp_Env_Vars(env_vars=env_vars) as _:
            auth_service = Service__Auth()
            result = auth_service.test_api_key()

            assert result["success"]         is True
            assert result["auth_configured"] is False


