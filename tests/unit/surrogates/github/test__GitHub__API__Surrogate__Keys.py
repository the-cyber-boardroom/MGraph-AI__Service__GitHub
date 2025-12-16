from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__Keys        import GitHub__API__Surrogate__Keys


class test__GitHub__API__Surrogate__Keys(TestCase):

    @cache_on_self
    def keys(self):
        return GitHub__API__Surrogate__Keys().setup()

    def test_key_generation(self):
        public_key = self.keys().get_or_create_key_pair("test_scope")

        assert public_key.key_id is not None
        assert public_key.key    is not None
        assert len(public_key.key) > 0                                              # Base64 encoded

    def test_encrypt_decrypt(self):
        scope_id  = "repo:owner/repo"
        plaintext = "my_secret_value"

        encrypted = self.keys().encrypt_secret(scope_id, plaintext)
        decrypted = self.keys().decrypt_secret(scope_id, encrypted)

        assert encrypted != plaintext
        assert decrypted == plaintext

    def test_scope_id_generation(self):
        assert self.keys().scope_id_for_repo("owner", "repo")        == "repo:owner/repo"
        assert self.keys().scope_id_for_env("owner", "repo", "prod") == "env:owner/repo/prod"
        assert self.keys().scope_id_for_org("my-org")                == "org:my-org"

    def test_convenience_methods(self):
        repo_key = self.keys().get_repo_public_key("owner", "repo")
        assert repo_key.key_id is not None

        env_key = self.keys().get_env_public_key("owner", "repo", "prod")
        assert env_key.key_id is not None

        org_key = self.keys().get_org_public_key("my-org")
        assert org_key.key_id is not None

        # Different scopes should have different keys
        assert repo_key.key_id != env_key.key_id
        assert env_key.key_id  != org_key.key_id