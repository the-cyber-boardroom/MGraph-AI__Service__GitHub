from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys        import GitHub__API__Surrogate__Keys


class test__GitHub__API__Surrogate__Keys(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.keys = GitHub__API__Surrogate__Keys().setup()

    def test_key_generation(self):
        public_key = self.keys.get_or_create_key_pair("test_scope")

        assert public_key.key_id is not None
        assert public_key.key    is not None
        assert len(public_key.key) > 0                                              # Base64 encoded

    def test_encrypt_decrypt(self):
        scope_id  = "repo:owner/repo"
        plaintext = "my_secret_value"

        encrypted = self.keys.encrypt_secret(scope_id, plaintext)
        decrypted = self.keys.decrypt_secret(scope_id, encrypted)

        assert encrypted != plaintext
        assert decrypted == plaintext

    def test_scope_id_generation(self):
        assert self.keys.scope_id_for_repo("owner", "repo")        == "repo:owner/repo"
        assert self.keys.scope_id_for_env("owner", "repo", "prod") == "env:owner/repo/prod"
        assert self.keys.scope_id_for_org("my-org")                == "org:my-org"

    def test_convenience_methods(self):
        repo_key = self.keys.get_repo_public_key("owner", "repo")
        assert repo_key.key_id is not None

        env_key = self.keys.get_env_public_key("owner", "repo", "prod")
        assert env_key.key_id is not None

        org_key = self.keys.get_org_public_key("my-org")
        assert org_key.key_id is not None

        # Different scopes should have different keys
        assert repo_key.key_id != env_key.key_id
        assert env_key.key_id  != org_key.key_id

    def test_reset(self):
        keys = GitHub__API__Surrogate__Keys().setup()

        # Create a key
        keys.get_or_create_key_pair("test_scope")
        assert keys.get_public_key("test_scope") is not None

        # Reset
        keys.reset()

        # Key should be gone
        assert keys.get_public_key("test_scope") is None

    def test_validate_encrypted_value_success(self):
        keys      = GitHub__API__Surrogate__Keys().setup()
        scope_id  = "repo:owner/repo"
        plaintext = "my_secret"

        encrypted = keys.encrypt_secret(scope_id, plaintext)
        is_valid  = keys.validate_encrypted_value(scope_id, encrypted)

        assert is_valid is True

    def test_validate_encrypted_value_failure(self):
        keys     = GitHub__API__Surrogate__Keys().setup()
        scope_id = "repo:owner/repo"

        # Create key pair
        keys.get_or_create_key_pair(scope_id)

        # Invalid encrypted value
        is_valid = keys.validate_encrypted_value(scope_id, "not_valid_encrypted_data")

        assert is_valid is False

    def test_decrypt_unknown_scope_raises(self):
        keys = GitHub__API__Surrogate__Keys().setup()

        with self.assertRaises(ValueError) as context:
            keys.decrypt_secret("unknown_scope", "some_data")

        assert "No key pair found" in str(context.exception)

    def test_get_key_id(self):
        keys     = GitHub__API__Surrogate__Keys().setup()
        scope_id = "repo:owner/repo"

        # Before creating key pair
        assert keys.get_key_id(scope_id) is None

        # After creating key pair
        keys.get_or_create_key_pair(scope_id)
        key_id = keys.get_key_id(scope_id)

        assert key_id is not None
        assert len(key_id) > 0