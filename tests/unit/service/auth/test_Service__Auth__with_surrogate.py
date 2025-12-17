import base64
from unittest                                                                               import TestCase
from nacl.public                                                                            import PrivateKey, PublicKey, SealedBox

from mgraph_ai_service_github.service.github.GitHub__API                                    import GitHub__API
import mgraph_ai_service_github.service.github.GitHub__API as github_api_module
from mgraph_ai_service_github.surrogates.github.testing.GitHub__API__Surrogate__Test_Context import GitHub__API__Surrogate__Test_Context


# ═══════════════════════════════════════════════════════════════════════════════
# Minimal NaCl key helper (for tests that don't have access to full test infra)
# ═══════════════════════════════════════════════════════════════════════════════

class NaCl__Test_Keys:                                                          # Simple NaCl key pair for testing
    def __init__(self):
        self._private_key = PrivateKey.generate()
        self._public_key  = self._private_key.public_key

    @property
    def private_key(self) -> str:
        return bytes(self._private_key).hex()

    @property
    def public_key(self) -> str:
        return bytes(self._public_key).hex()

    def encrypt(self, plaintext: str) -> str:                                   # Encrypt string and return base64
        sealed_box = SealedBox(self._public_key)
        encrypted  = sealed_box.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_b64: str) -> str:                               # Decrypt base64 string
        sealed_box = SealedBox(self._private_key)
        encrypted  = base64.b64decode(encrypted_b64)
        return sealed_box.decrypt(encrypted).decode('utf-8')


# ═══════════════════════════════════════════════════════════════════════════════
# Stub Service__Auth for this standalone test
# ═══════════════════════════════════════════════════════════════════════════════

class Service__Auth__Stub:                                                      # Simplified Service__Auth for demonstrating surrogate usage
    def __init__(self, private_key_hex: str, public_key_hex: str):
        self.private_key_hex = private_key_hex
        self.public_key_hex  = public_key_hex
        self._private_key    = PrivateKey(bytes.fromhex(private_key_hex))

    def decrypt_pat(self, encrypted_pat: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_pat)
        sealed_box      = SealedBox(self._private_key)
        return sealed_box.decrypt(encrypted_bytes).decode('utf-8')

    def test(self, encrypted_pat: str) -> dict:                                 # Test encrypted PAT against GitHub API
        response = {"success": False, "error": None, "error_type": None, "user": None, "rate_limit": None}

        if not encrypted_pat:
            response["error"]      = "Missing X-OSBot-GitHub-PAT header"
            response["error_type"] = "MISSING_HEADER"
            return response

        try:
            decrypted_pat = self.decrypt_pat(encrypted_pat)
        except Exception as e:
            response["error"]      = str(e)
            response["error_type"] = "DECRYPTION_FAILED"
            return response

        try:
            github_api      = GitHub__API(api_token=decrypted_pat)
            user_data       = github_api.get('/user')
            rate_limit_data = github_api.get('/rate_limit')

            response["success"] = True
            response["user"]    = {"login": user_data.get("login"), "id": user_data.get("id")}
            response["rate_limit"] = {"limit": rate_limit_data.get("rate", {}).get("limit"),
                                      "remaining": rate_limit_data.get("rate", {}).get("remaining")}
        except Exception as e:
            error_message = str(e)
            if "401" in error_message:
                response["error"]      = "GitHub API error: Bad credentials (401)"
                response["error_type"] = "INVALID_PAT"
            else:
                response["error"]      = f"GitHub API error: {error_message}"
                response["error_type"] = "GITHUB_ERROR"

        return response

    def test_github_pat(self, github_pat: str) -> dict:                         # Test plain PAT against GitHub API
        response = {"success": False, "error": None, "error_type": None, "user": None, "rate_limit": None}

        if not github_pat:
            response["error"]      = "GitHub PAT cannot be empty"
            response["error_type"] = "INVALID_INPUT"
            return response

        try:
            github_api      = GitHub__API(api_token=github_pat)
            user_data       = github_api.get('/user')
            rate_limit_data = github_api.get('/rate_limit')

            response["success"] = True
            response["user"]    = {"login": user_data.get("login"), "id": user_data.get("id")}
            response["rate_limit"] = {"limit": rate_limit_data.get("rate", {}).get("limit"),
                                      "remaining": rate_limit_data.get("rate", {}).get("remaining")}
        except Exception as e:
            error_message = str(e)
            if "401" in error_message:
                response["error"]      = "GitHub API error: Bad credentials (401)"
                response["error_type"] = "INVALID_PAT"
            else:
                response["error"]      = f"GitHub API error: {error_message}"
                response["error_type"] = "GITHUB_ERROR"

        return response


class test_Service__Auth__with_surrogate(TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup NaCl keys for encryption/decryption
        cls.nacl_keys    = NaCl__Test_Keys()
        cls.auth_service = Service__Auth__Stub(private_key_hex = cls.nacl_keys.private_key,
                                               public_key_hex  = cls.nacl_keys.public_key )

        # Setup surrogate - this wires GitHub__API to use surrogate
        cls.surrogate_context = GitHub__API__Surrogate__Test_Context().setup()

        # Get the admin PAT from surrogate for testing
        cls.surrogate_admin_pat = cls.surrogate_context.admin_pat()

    @classmethod
    def tearDownClass(cls):
        cls.surrogate_context.teardown()                                        # Clear session factory

    # ═══════════════════════════════════════════════════════════════════════════════
    # Verify surrogate is wired correctly
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_surrogate_is_active(self):
        assert github_api_module._session_factory is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test with valid surrogate PAT
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__success_with_surrogate(self):
        # Encrypt the surrogate admin PAT using our test keys
        encrypted_pat = self.nacl_keys.encrypt(self.surrogate_admin_pat)

        # Test using Service__Auth - it will:
        # 1. Decrypt the PAT → surrogate_admin_pat
        # 2. Create GitHub__API(api_token=surrogate_admin_pat)
        # 3. GitHub__API.session() → returns Requests__Session__Github__Surrogate
        # 4. Surrogate validates the PAT and returns user data
        result = self.auth_service.test(encrypted_pat)

        assert result["success"]       is True
        assert result["error"]         is None
        assert result["user"]          is not None
        assert result["user"]["login"] == "surrogate-admin"                     # Surrogate returns predictable user
        assert result["user"]["id"]    == 1000001
        assert result["rate_limit"]    is not None
        assert result["rate_limit"]["limit"] == 5000

    def test_test__success_user_details(self):
        encrypted_pat = self.nacl_keys.encrypt(self.surrogate_admin_pat)
        result        = self.auth_service.test(encrypted_pat)

        assert result["success"] is True
        assert "login" in result["user"]
        assert "id"    in result["user"]

    def test_test__success_rate_limit_details(self):
        encrypted_pat = self.nacl_keys.encrypt(self.surrogate_admin_pat)
        result        = self.auth_service.test(encrypted_pat)

        assert result["success"] is True
        assert result["rate_limit"]["limit"]     == 5000
        assert result["rate_limit"]["remaining"] == 4999

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test with invalid PAT (surrogate returns 401)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test__invalid_pat(self):
        # Encrypt an unknown PAT - surrogate will return 401
        encrypted_pat = self.nacl_keys.encrypt("ghp_unknown_invalid_token")

        result = self.auth_service.test(encrypted_pat)

        assert result["success"]    is False
        assert result["error_type"] == "INVALID_PAT"
        assert "Bad credentials"    in result["error"]

    def test_test__expired_pat(self):
        # Use surrogate's expired PAT
        expired_pat   = self.surrogate_context.expired_pat()
        encrypted_pat = self.nacl_keys.encrypt(expired_pat)

        result = self.auth_service.test(encrypted_pat)

        assert result["success"]    is False
        assert result["error_type"] == "INVALID_PAT"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test GitHub PAT directly (no encryption)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test_github_pat__success(self):
        result = self.auth_service.test_github_pat(self.surrogate_admin_pat)

        assert result["success"]       is True
        assert result["user"]["login"] == "surrogate-admin"

    def test_test_github_pat__invalid(self):
        result = self.auth_service.test_github_pat("ghp_invalid_pat_12345")

        assert result["success"]    is False
        assert result["error_type"] == "INVALID_PAT"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Test different PAT types from surrogate
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_test_github_pat__repo_write_user(self):
        result = self.auth_service.test_github_pat(self.surrogate_context.repo_write_pat())

        assert result["success"]       is True
        assert result["user"]["login"] == "surrogate-repo-write"

    def test_test_github_pat__org_admin_user(self):
        result = self.auth_service.test_github_pat(self.surrogate_context.org_admin_pat())

        assert result["success"]       is True
        assert result["user"]["login"] == "surrogate-org-admin"