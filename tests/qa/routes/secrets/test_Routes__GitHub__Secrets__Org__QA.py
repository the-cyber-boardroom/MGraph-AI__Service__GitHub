from unittest                                                           import TestCase
from osbot_utils.utils.Env                                              import get_env, load_dotenv
from mgraph_ai_service_github.utils.testing.QA__GitHub_Secrets_Client   import QA__GitHub_Secrets_Client
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client             import skip_if_no_service_url, skip_if_no_github_pat, setup__qa_test_objs

ENV_VAR__TESTS__GITHUB__REPO_OWNER = 'TESTS__GITHUB__REPO_OWNER'


class test_Routes__GitHub__Secrets__Org__QA(TestCase):                              # QA tests for /github-secrets-org/* routes

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        load_dotenv()

        cls.org_name = get_env(ENV_VAR__TESTS__GITHUB__REPO_OWNER)                  # Org is same as repo owner

        if not cls.org_name:
            import pytest
            pytest.skip(f"Missing {ENV_VAR__TESTS__GITHUB__REPO_OWNER}")

        with setup__qa_test_objs() as _:
            cls.secrets_client = QA__GitHub_Secrets_Client(http_client = _.http_client)

        # Check if we have org admin access by trying to list secrets
        result = cls.secrets_client.list_org_secrets(cls.org_name)
        if result.get('response_context', {}).get('status_code') in [403, 404]:
            import pytest
            pytest.skip(f"No org admin access for '{cls.org_name}' - skipping org secrets tests")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setUpClass(self):                                                     # Verify test setup completed correctly
        with self.secrets_client as _:
            assert type(_)           is QA__GitHub_Secrets_Client
            assert _.encrypted_pat() is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list__success(self):                                                  # POST /github-secrets-org/list - List org secrets
        with self.secrets_client as _:
            result = _.list_org_secrets(self.org_name)

            assert result.get('response_context', {}).get('success')     is True
            assert result.get('response_context', {}).get('status_code') == 200
            assert result.get('response_data', {}).get('secrets')        is not None
            assert type(result.get('response_data', {}).get('secrets'))  is list

            # Verify rate limit info is populated
            rate_limit = result.get('response_context', {}).get('rate_limit', {})
            assert rate_limit.get('limit')     is not None
            assert rate_limit.get('remaining') is not None

            secrets = result.get('response_data', {}).get('secrets', [])
            print(f"\n  ✓ Found {len(secrets)} org secrets in '{self.org_name}'")
            for secret in secrets[:5]:
                print(f"    - {secret.get('name')} (visibility: {secret.get('visibility')})")

    def test__list__invalid_org(self):                                              # POST /github-secrets-org/list - Invalid org returns 404/403
        with self.secrets_client as _:
            result = _.list_org_secrets('nonexistent-org-xyz-12345')

            assert result.get('response_context', {}).get('success')     is False
            assert result.get('response_context', {}).get('status_code') in [403, 404]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Get Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get__not_found(self):                                                 # POST /github-secrets-org/get - Nonexistent secret
        with self.secrets_client as _:
            result = _.get_org_secret(self.org_name, 'NONEXISTENT_SECRET_XYZ')

            assert result.get('response_context', {}).get('success')     is False
            assert result.get('response_context', {}).get('status_code') == 404
            assert result.get('response_context', {}).get('error_type')  == 'not_found'

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full CRUD Lifecycle Test
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__full_secret_lifecycle(self):                                          # Create -> Get -> Update -> Delete
        secret_name  = 'QA_ORG_TEST_SECRET_TEMP'
        secret_value = 'qa_org_test_value_123'

        with self.secrets_client as _:
            # Step 1: Create with visibility='private'
            create_result = _.create_org_secret(self.org_name, secret_name, secret_value, visibility='private')

            assert create_result.get('response_context', {}).get('success')     is True
            assert create_result.get('response_context', {}).get('status_code') == 201
            assert create_result.get('response_data', {}).get('created')        is True
            print(f"\n  ✓ Created org secret: {secret_name}")

            # Step 2: Get
            get_result = _.get_org_secret(self.org_name, secret_name)

            assert get_result.get('response_context', {}).get('success')       is True
            assert get_result.get('response_context', {}).get('status_code')   == 200
            secret_data = get_result.get('response_data', {}).get('secret', {})
            assert secret_data.get('name')       == secret_name
            assert secret_data.get('visibility') == 'private'
            print(f"  ✓ Retrieved org secret: {secret_name} (visibility: {secret_data.get('visibility')})")

            # Step 3: Update
            updated_value = 'qa_org_updated_value_456'
            update_result = _.update_org_secret(self.org_name, secret_name, updated_value, visibility='private')

            assert update_result.get('response_context', {}).get('success')     is True
            assert update_result.get('response_context', {}).get('status_code') == 200
            assert update_result.get('response_data', {}).get('updated')        is True
            print(f"  ✓ Updated org secret: {secret_name}")

            # Step 4: Delete
            delete_result = _.delete_org_secret(self.org_name, secret_name)

            assert delete_result.get('response_context', {}).get('success')     is True
            assert delete_result.get('response_context', {}).get('status_code') == 200
            assert delete_result.get('response_data', {}).get('deleted')        is True
            print(f"  ✓ Deleted org secret: {secret_name}")

            # Step 5: Verify deletion
            verify_result = _.get_org_secret(self.org_name, secret_name)

            assert verify_result.get('response_context', {}).get('success')     is False
            assert verify_result.get('response_context', {}).get('status_code') == 404
            print(f"  ✓ Verified deletion: {secret_name}")

    def test__create_with_visibility_all(self):                                     # Create with visibility='all'
        secret_name  = 'QA_ORG_VIS_ALL_TEMP'
        secret_value = 'qa_org_vis_all_value'

        with self.secrets_client as _:
            # Create with visibility='all'
            create_result = _.create_org_secret(self.org_name, secret_name, secret_value, visibility='all')

            assert create_result.get('response_context', {}).get('success')     is True
            assert create_result.get('response_context', {}).get('status_code') == 201
            print(f"\n  ✓ Created org secret with visibility='all': {secret_name}")

            # Verify visibility
            get_result = _.get_org_secret(self.org_name, secret_name)
            assert get_result.get('response_data', {}).get('secret', {}).get('visibility') == 'all'
            print(f"  ✓ Verified visibility='all'")

            # Cleanup
            delete_result = _.delete_org_secret(self.org_name, secret_name)
            assert delete_result.get('response_context', {}).get('success') is True
            print(f"  ✓ Cleaned up: {secret_name}")