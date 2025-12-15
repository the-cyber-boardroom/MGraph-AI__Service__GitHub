from unittest                                                         import TestCase
from osbot_utils.utils.Env                                            import get_env, load_dotenv
from mgraph_ai_service_github.config                                  import ENV_VAR__TESTS__GITHUB__REPO_OWNER, ENV_VAR__TESTS__GITHUB__REPO_NAME
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client           import skip_if_no_service_url, skip_if_no_github_pat, setup__qa_test_objs
from mgraph_ai_service_github.utils.testing.QA__GitHub_Secrets_Client import QA__GitHub_Secrets_Client



class test_Routes__GitHub__Secrets__Repo__QA(TestCase):                             # QA tests for /github-secrets-repo/* routes

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        load_dotenv()

        cls.repo_owner = get_env(ENV_VAR__TESTS__GITHUB__REPO_OWNER)
        cls.repo_name  = get_env(ENV_VAR__TESTS__GITHUB__REPO_NAME)

        if not cls.repo_owner or not cls.repo_name:
            import pytest
            pytest.skip(f"Missing {ENV_VAR__TESTS__GITHUB__REPO_OWNER} or {ENV_VAR__TESTS__GITHUB__REPO_NAME}")

        with setup__qa_test_objs() as _:
            cls.secrets_client = QA__GitHub_Secrets_Client(http_client = _.http_client)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):                                                     # Verify test setup completed correctly
        with self.secrets_client as _:
            assert type(_)          is QA__GitHub_Secrets_Client
            assert _.encrypted_pat() is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list__success(self):                                                  # POST /github-secrets-repo/list - List repo secrets
        with self.secrets_client as _:
            result = _.list_repo_secrets(self.repo_owner, self.repo_name)

            assert result.get('response_context', {}).get('success')     is True
            assert result.get('response_context', {}).get('status_code') == 200
            assert result.get('response_data', {}).get('secrets')        is not None
            assert type(result.get('response_data', {}).get('secrets'))  is list

            # Verify rate limit info is populated
            rate_limit = result.get('response_context', {}).get('rate_limit', {})
            assert rate_limit.get('limit')     is not None
            assert rate_limit.get('remaining') is not None

            secrets = result.get('response_data', {}).get('secrets', [])
            print(f"\n  ✓ Found {len(secrets)} repo secrets")
            for secret in secrets[:5]:                                              # Show first 5
                print(f"    - {secret.get('name')}")

    def test__list__invalid_repo(self):                                             # POST /github-secrets-repo/list - Invalid repo returns 404
        with self.secrets_client as _:
            result = _.list_repo_secrets(self.repo_owner, 'nonexistent-repo-xyz-12345')

            assert result.get('response_context', {}).get('success')     is False
            assert result.get('response_context', {}).get('status_code') == 404
            assert result.get('response_context', {}).get('error_type')  == 'not_found'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get__not_found(self):                                                 # POST /github-secrets-repo/get - Nonexistent secret
        with self.secrets_client as _:
            result = _.get_repo_secret(self.repo_owner, self.repo_name, 'NONEXISTENT_SECRET_XYZ')

            assert result.get('response_context', {}).get('success')     is False
            assert result.get('response_context', {}).get('status_code') == 404
            assert result.get('response_context', {}).get('error_type')  == 'not_found'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full CRUD Lifecycle Test
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__full_secret_lifecycle(self):                                          # Create -> Get -> Update -> Delete
        secret_name  = 'QA_TEST_SECRET_TEMP'
        secret_value = 'qa_test_value_123'

        with self.secrets_client as _:
            # Step 1: Create
            create_result = _.create_repo_secret(self.repo_owner, self.repo_name, secret_name, secret_value)

            assert create_result.get('response_context', {}).get('success')     is True
            assert create_result.get('response_context', {}).get('status_code') == 201
            assert create_result.get('response_data', {}).get('created')        is True
            print(f"\n  ✓ Created secret: {secret_name}")

            # Step 2: Get
            get_result = _.get_repo_secret(self.repo_owner, self.repo_name, secret_name)

            assert get_result.get('response_context', {}).get('success')       is True
            assert get_result.get('response_context', {}).get('status_code')   == 200
            assert get_result.get('response_data', {}).get('secret', {}).get('name') == secret_name
            print(f"  ✓ Retrieved secret: {secret_name}")

            # Step 3: Update
            updated_value = 'qa_updated_value_456'
            update_result = _.update_repo_secret(self.repo_owner, self.repo_name, secret_name, updated_value)

            assert update_result.get('response_context', {}).get('success')     is True
            assert update_result.get('response_context', {}).get('status_code') == 200
            assert update_result.get('response_data', {}).get('updated')        is True
            print(f"  ✓ Updated secret: {secret_name}")

            # Step 4: Delete
            delete_result = _.delete_repo_secret(self.repo_owner, self.repo_name, secret_name)

            assert delete_result.get('response_context', {}).get('success')     is True
            assert delete_result.get('response_context', {}).get('status_code') == 200
            assert delete_result.get('response_data', {}).get('deleted')        is True
            print(f"  ✓ Deleted secret: {secret_name}")

            # Step 5: Verify deletion
            verify_result = _.get_repo_secret(self.repo_owner, self.repo_name, secret_name)

            assert verify_result.get('response_context', {}).get('success')     is False
            assert verify_result.get('response_context', {}).get('status_code') == 404
            print(f"  ✓ Verified deletion: {secret_name}")