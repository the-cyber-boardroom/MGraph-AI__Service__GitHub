from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate              import GitHub__API__Surrogate
from mgraph_ai_service_github.service.github.GitHub__API                            import GitHub__API


class test__GitHub__API__Surrogate__Integration(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.surrogate = (GitHub__API__Surrogate()
                .setup()
                .add_repo("test-org", "test-repo")
                .add_secret("test-org", "test-repo", "EXISTING_KEY"))
     

    def test_create_api(self):
        github_api = self.surrogate.create_api()

        # Should work through surrogate
        user_data = github_api.get('/user')
        assert user_data['login'] == 'surrogate-admin'

        rate_limit = github_api.get('/rate_limit')
        assert rate_limit['rate']['limit'] == 5000

    def test_create_secrets(self):
        github_secrets = self.surrogate.create_secrets(repo_name="test-org/test-repo")

        # List secrets
        secrets = github_secrets.list_secrets()
        assert len(secrets) >= 1
        assert any(s['name'] == 'EXISTING_KEY' for s in secrets)

        # Create new secret
        result = github_secrets.create_or_update_secret('NEW_KEY', 'new_value')
        assert result is True

        # Verify
        secrets = github_secrets.list_secrets()
        assert any(s['name'] == 'NEW_KEY' for s in secrets)

        # Get secret
        secret = github_secrets.get_secret('NEW_KEY')
        assert secret is not None
        assert secret['name'] == 'NEW_KEY'

        # Delete secret
        result = github_secrets.delete_secret('NEW_KEY')
        assert result is True

    def test_inject_existing_api(self):
        pats       = self.surrogate.pats
        github_api = GitHub__API(api_token=pats.repo_write_pat())

        # Inject surrogate
        self.surrogate.inject(github_api)

        # Should work through surrogate with correct permissions
        user_data = github_api.get('/user')
        assert user_data['login'] == 'surrogate-repo-write'

    def test_reset(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_repo("owner", "repo")
        surrogate.add_secret("owner", "repo", "SECRET")

        assert surrogate.state.repo_exists("owner", "repo") is True

        surrogate.reset()

        assert surrogate.state.repo_exists("owner", "repo") is False

    def test_encrypt_for_repo(self):
        surrogate  = GitHub__API__Surrogate().setup()
        surrogate.add_repo("owner", "repo")

        encrypted = surrogate.encrypt_for_repo("owner", "repo", "my_secret")

        assert encrypted is not None
        assert encrypted != "my_secret"
        assert len(encrypted) > 0

    def test_encrypt_for_env(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_repo("owner", "repo")
        surrogate.add_environment("owner", "repo", "production")

        encrypted = surrogate.encrypt_for_env("owner", "repo", "production", "my_secret")

        assert encrypted is not None
        assert encrypted != "my_secret"
        assert len(encrypted) > 0

    def test_encrypt_for_org(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_org("my-org")

        encrypted = surrogate.encrypt_for_org("my-org", "my_secret")

        assert encrypted is not None
        assert encrypted != "my_secret"
        assert len(encrypted) > 0

    def test_get_repo_key_id(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_repo("owner", "repo")

        key_id = surrogate.get_repo_key_id("owner", "repo")

        assert key_id is not None
        assert len(key_id) > 0

    def test_get_env_key_id(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_repo("owner", "repo")
        surrogate.add_environment("owner", "repo", "staging")

        key_id = surrogate.get_env_key_id("owner", "repo", "staging")

        assert key_id is not None
        assert len(key_id) > 0

    def test_get_org_key_id(self):
        surrogate = GitHub__API__Surrogate().setup()
        surrogate.add_org("my-org")

        key_id = surrogate.get_org_key_id("my-org")

        assert key_id is not None
        assert len(key_id) > 0

    def test_app_and_test_client(self):
        surrogate = GitHub__API__Surrogate().setup()

        assert surrogate.app()         is not None
        assert surrogate.test_client() is not None

    def test_create_session(self):
        surrogate = GitHub__API__Surrogate().setup()

        # With default (admin) PAT
        session = surrogate.create_session()
        assert session is not None

        # With specific PAT
        session = surrogate.create_session(surrogate.pats.repo_write_pat())
        assert session is not None

    def test_create_secrets_default_repo_name(self):
        # Covers line 117: repo_name is None default
        surrogate      = GitHub__API__Surrogate().setup()
        surrogate.add_repo("test-owner", "test-repo")

        github_secrets = surrogate.create_secrets()                             # No repo_name provided

        assert github_secrets.repo_name == "test-owner/test-repo"
