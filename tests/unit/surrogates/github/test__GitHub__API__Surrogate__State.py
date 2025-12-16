from unittest                                                                     import TestCase
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State     import GitHub__API__Surrogate__State

class test__GitHub__API__Surrogate__State(TestCase):

    def test_repo_operations(self):
        state = GitHub__API__Surrogate__State()

        # Add repo
        state.add_repo("test-owner", "test-repo")
        assert state.repo_exists("test-owner", "test-repo") is True
        assert state.repo_exists("other", "repo")           is False

        # Get repo
        repo = state.get_repo("test-owner", "test-repo")
        assert repo.owner     == "test-owner"
        assert repo.name      == "test-repo"
        assert repo.full_name == "test-owner/test-repo"

    def test_environment_operations(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "production")

        assert state.environment_exists("owner", "repo", "production") is True
        assert state.environment_exists("owner", "repo", "staging")    is False

    def test_repo_secret_operations(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")

        # Set secret
        state.set_repo_secret("owner", "repo", "API_KEY", "encrypted_value", "key_123")

        # Get secret
        secret = state.get_repo_secret("owner", "repo", "API_KEY")
        assert secret is not None
        assert secret.name            == "API_KEY"
        assert secret.encrypted_value == "encrypted_value"

        # List secrets
        secrets = state.list_repo_secrets("owner", "repo")
        assert len(secrets) == 1

        # Delete secret
        deleted = state.delete_repo_secret("owner", "repo", "API_KEY")
        assert deleted is True
        assert state.get_repo_secret("owner", "repo", "API_KEY") is None

    def test_env_secret_operations(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "prod")

        # Set secret
        state.set_env_secret("owner", "repo", "prod", "DB_PASS", "encrypted", "key_1")

        # Get secret
        secret = state.get_env_secret("owner", "repo", "prod", "DB_PASS")
        assert secret is not None
        assert secret.name == "DB_PASS"

        # List secrets
        secrets = state.list_env_secrets("owner", "repo", "prod")
        assert len(secrets) == 1

        # Delete
        state.delete_env_secret("owner", "repo", "prod", "DB_PASS")
        assert state.get_env_secret("owner", "repo", "prod", "DB_PASS") is None

    def test_org_secret_operations(self):
        state = GitHub__API__Surrogate__State()
        state.add_org("test-org")

        # Set secret
        state.set_org_secret("test-org", "ORG_KEY", "encrypted", "key_1", "private")

        # Get secret
        secret = state.get_org_secret("test-org", "ORG_KEY")
        assert secret is not None
        assert secret.name       == "ORG_KEY"
        assert secret.visibility == "private"

        # Delete
        state.delete_org_secret("test-org", "ORG_KEY")
        assert state.get_org_secret("test-org", "ORG_KEY") is None

    def test_reset(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.set_repo_secret("owner", "repo", "KEY", "val", "id")

        state.reset()

        assert state.repo_exists("owner", "repo") is False






