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

class test_Service__Auth__with_github_pat(TestCase):                                            # Tests requiring real GitHub PAT

    @classmethod
    def setUpClass(cls):
        cls.nacl_keys        = create_and_set_nacl_keys()
        cls.auth_service     = Service__Auth(private_key_hex = cls.nacl_keys.private_key,
                                             public_key_hex  = cls.nacl_keys.public_key)
        cls.surrogate_context = GitHub__API__Surrogate__Test_Context().setup()
        cls.github_pat        = cls.surrogate_context.admin_pat()                       # Use surrogate PAT

    @classmethod
    def tearDownClass(cls):
        cls.surrogate_context.teardown()

    @classmethod
    def _encrypt_pat(cls, pat            : str ,
                          public_key_hex : str
                     ) -> str:
        public_key = PublicKey(bytes.fromhex(public_key_hex))
        sealed_box = SealedBox(public_key)
        encrypted  = sealed_box.encrypt(pat.encode('utf-8'))

        return base64.b64encode(encrypted).decode('utf-8')

    def setUp(self):
        if not self.github_pat:
            self.skipTest("GIT_HUB__ACCESS_TOKEN not set")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test Method - Success with Real GitHub PAT
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__success(self):                                                               # Test test() with real GitHub PAT
        encrypted_pat = self._encrypt_pat(self.github_pat, self.nacl_keys.public_key)

        with self.auth_service as _:
            result = _.test(encrypted_pat)

            assert result["success"]                 is True
            assert result["error"]                   is None
            assert result["error_type"]              is None
            assert result["user"]                    is not None
            assert result["user"]["login"]           is not None
            assert result["user"]["id"]              is not None
            assert result["rate_limit"]              is not None
            assert result["rate_limit"]["limit"]     is not None
            assert result["rate_limit"]["remaining"] is not None

    def test_test__success__user_details(self):                                                 # Test test() returns full user details
        encrypted_pat = self._encrypt_pat(self.github_pat, self.nacl_keys.public_key)

        with self.auth_service as _:
            result = _.test(encrypted_pat)

            assert result["success"] is True

            user = result["user"]
            assert "login"       in user
            assert "id"          in user
            assert "name"        in user
            assert "created_at"  in user
            assert "public_repos" in user

    def test_test__success__rate_limit_details(self):                                           # Test test() returns rate limit details
        encrypted_pat = self._encrypt_pat(self.github_pat, self.nacl_keys.public_key)

        with self.auth_service as _:
            result = _.test(encrypted_pat)

            assert result["success"] is True

            rate_limit = result["rate_limit"]
            assert "limit"     in rate_limit
            assert "remaining" in rate_limit
            assert "reset"     in rate_limit
            assert "used"      in rate_limit

            assert rate_limit["limit"]     >= 5000                                              # Authenticated users get at least 5000
            assert rate_limit["remaining"] <= rate_limit["limit"]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test GitHub PAT - Success Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test_github_pat__success(self):                                                    # Test test_github_pat() with real PAT
        with self.auth_service as _:
            result = _.test_github_pat(self.github_pat)

            assert result["success"]       is True
            assert result["user"]          is not None
            assert result["user"]["login"] is not None
            assert result["rate_limit"]    is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Flow Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__full_encrypt_decrypt_validate_flow(self):                                         # Test complete PAT encryption and validation flow
        with self.auth_service as _:
            # Step 1: Encrypt PAT
            encrypted = _.encrypt_pat(self.github_pat)
            assert encrypted is not None

            # Step 2: Decrypt and verify
            decrypted = _.decrypt_pat(encrypted)
            assert decrypted == self.github_pat

            # Step 3: Test with GitHub API
            result = _.test(encrypted)
            assert result["success"]       is True
            assert result["user"]["login"] is not None

            print(f"\n  ✓ Validated PAT for user: {result['user']['login']}")
            print(f"  ✓ Rate limit: {result['rate_limit']['remaining']}/{result['rate_limit']['limit']}")