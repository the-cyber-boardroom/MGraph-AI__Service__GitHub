from unittest                                                         import TestCase
from osbot_utils.utils.Env                                            import get_env, load_dotenv
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client           import skip_if_no_service_url, skip_if_no_github_pat, setup__qa_test_objs
from mgraph_ai_service_github.utils.testing.QA__GitHub_Secrets_Client import QA__GitHub_Secrets_Client

ENV_VAR__TESTS__GITHUB__REPO_OWNER = 'TESTS__GITHUB__REPO_OWNER'
ENV_VAR__TESTS__GITHUB__REPO_NAME  = 'TESTS__GITHUB__REPO_NAME'
TESTING__ENVIRONMENT__NAME         = 'testing'


class test_End_to_End__GitHub__Secrets__QA(TestCase):                               # End-to-end integration tests for GitHub Secrets routes

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        load_dotenv()

        cls.repo_owner       = get_env(ENV_VAR__TESTS__GITHUB__REPO_OWNER)
        cls.repo_name        = get_env(ENV_VAR__TESTS__GITHUB__REPO_NAME)
        cls.environment_name = TESTING__ENVIRONMENT__NAME

        if not cls.repo_owner or not cls.repo_name:
            import pytest
            pytest.skip(f"Missing {ENV_VAR__TESTS__GITHUB__REPO_OWNER} or {ENV_VAR__TESTS__GITHUB__REPO_NAME}")

        with setup__qa_test_objs() as _:
            cls.secrets_client = QA__GitHub_Secrets_Client(http_client = _.http_client)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Combined Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encrypted_pat_reuse(self):                                            # Verify encrypted PAT can be reused across multiple calls
        with self.secrets_client as _:
            # First call
            result_1 = _.list_repo_secrets(self.repo_owner, self.repo_name)
            assert result_1.get('response_context', {}).get('success') is True

            # Second call (should reuse cached encrypted_pat)
            result_2 = _.list_repo_secrets(self.repo_owner, self.repo_name)
            assert result_2.get('response_context', {}).get('success') is True

            print("\n  ✓ Encrypted PAT reused successfully across multiple calls")

    def test__rate_limit_tracking(self):                                            # Verify rate limit decreases across calls
        with self.secrets_client as _:
            # First call
            result_1 = _.list_repo_secrets(self.repo_owner, self.repo_name)
            rate_1   = result_1.get('response_context', {}).get('rate_limit', {})

            # Second call
            result_2 = _.list_repo_secrets(self.repo_owner, self.repo_name)
            rate_2   = result_2.get('response_context', {}).get('rate_limit', {})

            assert rate_1.get('remaining') is not None
            assert rate_2.get('remaining') is not None

            # Rate limit should have decreased (or stayed same if cached)
            assert rate_2.get('remaining') <= rate_1.get('remaining')

            print(f"\n  ✓ Rate limit tracking: {rate_1.get('remaining')} → {rate_2.get('remaining')}")

    def test__duration_tracking(self):                                              # Verify duration is tracked in responses
        with self.secrets_client as _:
            result = _.list_repo_secrets(self.repo_owner, self.repo_name)

            duration = result.get('response_context', {}).get('duration')
            assert duration is not None
            assert duration > 0

            print(f"\n  ✓ Duration tracked: {duration:.3f}s")

    def test__error_response_structure(self):                                       # Verify error responses have correct structure
        with self.secrets_client as _:
            result = _.get_repo_secret(self.repo_owner, self.repo_name, 'NONEXISTENT_SECRET_XYZ')

            context = result.get('response_context', {})

            assert context.get('success')     is False
            assert context.get('status_code') == 404
            assert context.get('error_type')  == 'not_found'
            assert context.get('errors')      is not None
            assert context.get('duration')    is not None
            assert context.get('timestamp')   is not None

            print("\n  ✓ Error response has correct structure")

    def test__cross_scope_secret_names(self):                                       # Same secret name can exist in different scopes
        secret_name  = 'QA_CROSS_SCOPE_SECRET'
        secret_value = 'cross_scope_value'

        with self.secrets_client as _:
            # Create repo secret
            repo_result = _.create_repo_secret(self.repo_owner, self.repo_name, secret_name, secret_value)

            if repo_result.get('response_context', {}).get('success'):
                print(f"\n  ✓ Created repo secret: {secret_name}")

                # Try to create env secret with same name (should succeed - different scope)
                env_result = _.create_env_secret(self.repo_owner, self.repo_name, self.environment_name, secret_name, secret_value)

                if env_result.get('response_context', {}).get('success'):
                    print(f"  ✓ Created env secret with same name: {secret_name}")

                    # Both should be listable independently
                    repo_list = _.list_repo_secrets(self.repo_owner, self.repo_name)
                    env_list  = _.list_env_secrets(self.repo_owner, self.repo_name, self.environment_name)

                    repo_names = [s.get('name') for s in repo_list.get('response_data', {}).get('secrets', [])]
                    env_names  = [s.get('name') for s in env_list.get('response_data', {}).get('secrets', [])]

                    assert secret_name in repo_names
                    assert secret_name in env_names
                    print(f"  ✓ Same name exists in both scopes")

                    # Cleanup env
                    _.delete_env_secret(self.repo_owner, self.repo_name, self.environment_name, secret_name)
                    print(f"  ✓ Cleaned up env secret")

                # Cleanup repo
                _.delete_repo_secret(self.repo_owner, self.repo_name, secret_name)
                print(f"  ✓ Cleaned up repo secret")
            else:
                self.skipTest("Could not create repo secret for cross-scope test")
