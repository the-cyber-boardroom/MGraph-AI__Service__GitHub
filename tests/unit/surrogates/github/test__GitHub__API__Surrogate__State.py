from unittest                                                                           import TestCase
from osbot_utils.testing.__                                                             import __
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__Dict                   import Type_Safe__Dict
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__State           import GitHub__API__Surrogate__State
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Public_Key   import Schema__Surrogate__Public_Key


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

    def test_add_repo_with_environments(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo", private=True, environments=["prod", "staging"])

        repo = state.get_repo("owner", "repo")
        assert repo.private is True
        assert "prod"    in repo.environments
        assert "staging" in repo.environments

    def test_env_secret_no_existing(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "prod")

        # Set secret when none exists
        result = state.set_env_secret("owner", "repo", "prod", "NEW_SECRET", "encrypted", "key_1")
        assert result is True

        # Verify
        secret = state.get_env_secret("owner", "repo", "prod", "NEW_SECRET")
        assert secret is not None
        assert secret.name == "NEW_SECRET"

    def test_env_secret_update_existing(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "prod")

        # Create
        state.set_env_secret("owner", "repo", "prod", "SECRET", "encrypted_v1", "key_1")

        # Update
        state.set_env_secret("owner", "repo", "prod", "SECRET", "encrypted_v2", "key_2")

        secret = state.get_env_secret("owner", "repo", "prod", "SECRET")
        assert secret.encrypted_value == "encrypted_v2"
        assert secret.key_id          == "key_2"

    def test_org_secret_update_existing(self):
        state = GitHub__API__Surrogate__State()
        state.add_org("my-org")

        # Create
        state.set_org_secret("my-org", "SECRET", "encrypted_v1", "key_1", "private")

        # Update with new visibility
        state.set_org_secret("my-org", "SECRET", "encrypted_v2", "key_2", "all")

        secret = state.get_org_secret("my-org", "SECRET")
        assert secret.encrypted_value == "encrypted_v2"
        assert secret.visibility      == "all"

    def test_public_key_operations(self):

        state = GitHub__API__Surrogate__State()

        public_key = Schema__Surrogate__Public_Key(key_id="123", key="base64key")
        state.set_public_key("repo:owner/repo", public_key)

        retrieved = state.get_public_key("repo:owner/repo")
        assert retrieved.key_id == "123"
        assert retrieved.key    == "base64key"

        # Non-existent
        assert state.get_public_key("unknown") is None

    def test_rate_limit_operations(self):
        state = GitHub__API__Surrogate__State()

        # Get creates default
        rate_limit = state.get_rate_limit("pat_123")
        assert rate_limit.limit     == 5000
        assert rate_limit.remaining == 4999

        # Same PAT returns same object
        rate_limit_2 = state.get_rate_limit("pat_123")
        assert rate_limit_2 is rate_limit


    def test_add_environment_creates_secrets_dict(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")

        # Add environment when secrets__env[repo_key] doesn't have this env yet
        state.add_environment("owner", "repo", "new_env")

        assert state.environment_exists("owner", "repo", "new_env") is True
        # Verify the nested dict was created
        assert "new_env" in state.secrets__env.get("owner/repo", {})

    def test_add_environment_to_nonexistent_repo(self):
        state = GitHub__API__Surrogate__State()

        # Add environment to repo that doesn't exist - should not crash
        state.add_environment("nonexistent", "repo", "prod")

        # Environment should not exist since repo doesn't exist
        assert state.environment_exists("nonexistent", "repo", "prod") is False

    def test_delete_env_secret_nonexistent(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "prod")

        # Delete from empty env - should return False
        result = state.delete_env_secret("owner", "repo", "prod", "NONEXISTENT")
        assert result is False

    def test_list_org_secrets_empty(self):
        state = GitHub__API__Surrogate__State()

        # List from nonexistent org - should return empty list
        secrets = state.list_org_secrets("nonexistent-org")
        assert secrets == []



    def test_set_env_secret_initializes_all_dicts(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "staging")

        # Clear secrets__env to force initialization paths
        state.secrets__env = {}

        result = state.set_env_secret("owner", "repo", "staging", "SECRET", "encrypted", "key123")

        assert result is True
        assert "owner/repo" in state.secrets__env
        assert "staging" in state.secrets__env["owner/repo"]
        assert "SECRET" in state.secrets__env["owner/repo"]["staging"]

    def test_set_env_secret_initializes_environment_dict_only(self):
        state = GitHub__API__Surrogate__State()
        state.add_repo("owner", "repo")
        state.add_environment("owner", "repo", "prod")

        # Set up secrets__env with repo_key but without the target environment
        state.secrets__env = {"owner/repo": {"other_env": {}}}

        # This should only create secrets__env["owner/repo"]["prod"] = {}
        result = state.set_env_secret("owner", "repo", "prod", "MY_SECRET", "encrypted", "key456")

        assert result is True
        assert "prod" in state.secrets__env["owner/repo"]
        assert "MY_SECRET" in state.secrets__env["owner/repo"]["prod"]

    def test_set_org_secret_initializes_org_dict(self):
        state = GitHub__API__Surrogate__State()

        # Ensure secrets__org doesn't have this org yet
        assert "my-org" not in state.secrets__org

        # This should create secrets__org["my-org"] = {}
        result = state.set_org_secret("my-org", "ORG_TOKEN", "encrypted_value", "key789", "private")

        assert result is True
        assert "my-org" in state.secrets__org
        assert "ORG_TOKEN" in state.secrets__org["my-org"]

    def test_set_repo_secret_initializes_org_dict(self):
        with GitHub__API__Surrogate__State() as _:
            repo_key = _._repo_key("owner", "repo")

            assert repo_key not in _.secrets__org

            result = _.set_repo_secret("owner", "repo", "API_KEY", "encrypted_value", "key_123")

            assert result is True
            assert type(_.secrets__repo) is Type_Safe__Dict
            assert _.secrets__repo.obj() == __(owner_repo=__(API_KEY=__(created_at='2024-01-15T10:30:00Z',
                                                                        updated_at='2024-01-15T10:30:00Z',
                                                                        encrypted_value='encrypted_value',
                                                                        key_id='key_123',
                                                                        name='API_KEY')))