from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate              import GitHub__API__Surrogate
from mgraph_ai_service_github.service.github.GitHub__API                            import GitHub__API


class test__GitHub__API__Surrogate__Integration(TestCase):

    @cache_on_self
    def surrogate(self):
        return (GitHub__API__Surrogate()
                .setup()
                .add_repo("test-org", "test-repo")
                .add_secret("test-org", "test-repo", "EXISTING_KEY"))

    def test_create_api(self):
        github_api = self.surrogate().create_api()

        # Should work through surrogate
        user_data = github_api.get('/user')
        assert user_data['login'] == 'surrogate-admin'

        rate_limit = github_api.get('/rate_limit')
        assert rate_limit['rate']['limit'] == 5000

    def test_create_secrets(self):
        github_secrets = self.surrogate().create_secrets(repo_name="test-org/test-repo")

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
        pats       = self.surrogate().pats
        github_api = GitHub__API(api_token=pats.repo_write_pat())

        # Inject surrogate
        self.surrogate().inject(github_api)

        # Should work through surrogate with correct permissions
        user_data = github_api.get('/user')
        assert user_data['login'] == 'surrogate-repo-write'