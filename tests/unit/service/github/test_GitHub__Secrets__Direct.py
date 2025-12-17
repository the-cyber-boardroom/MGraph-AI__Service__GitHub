import pytest
from unittest                                                import TestCase
from osbot_fast_api_serverless.utils.testing.skip_tests      import skip__if_not__in_github_actions
from requests.exceptions                                     import HTTPError
from osbot_utils.utils.Env                                   import get_env, load_dotenv
from osbot_utils.utils.Misc                                  import random_string
from mgraph_ai_service_github.service.github.GitHub__API     import GitHub__API
from mgraph_ai_service_github.service.github.GitHub__Secrets import GitHub__Secrets
from mgraph_ai_service_github.surrogates.github.testing.GitHub__API__Surrogate__Test_Context import GitHub__API__Surrogate__Test_Context

DEFAULT_GITHUB__REPO_OWNER = 'the-cyber-boardroom'
DEFAULT_GITHUB__REPO_NAME  = 'MGraph-AI__Service__GitHub'


class test_GitHub__Secrets(TestCase):

    # @classmethod
    # def setUpClass(cls):                                                                        # Setup test configuration
    #     #skip__if_not__in_github_actions()
    #     load_dotenv()
    #     cls.test_repo_owner = get_env('GITHUB_TEST_REPO_OWNER', DEFAULT_GITHUB__REPO_OWNER)
    #     cls.test_repo_name  = get_env('GITHUB_TEST_REPO_NAME' , DEFAULT_GITHUB__REPO_NAME)
    #     cls.test_repo       = f'{cls.test_repo_owner}/{cls.test_repo_name}'
    #     cls.api_token       = get_env('GIT_HUB__ACCESS_TOKEN')

    @classmethod
    def setUpClass(cls):
        cls.test_repo_owner   = 'test-owner'                                          # Use fixed test values
        cls.test_repo_name    = 'test-repo'
        cls.test_repo         = f'{cls.test_repo_owner}/{cls.test_repo_name}'

        cls.surrogate_context = GitHub__API__Surrogate__Test_Context().setup()      # Setup surrogate
        cls.api_token         = cls.surrogate_context.admin_pat()

        cls.surrogate_context.add_repo(cls.test_repo_owner, cls.test_repo_name)     # Add test repo to surrogate state


    def setUp(self):                                                              # Initialize test fixtures
        self.github_secrets = GitHub__Secrets(repo_name = self.test_repo ,
                                              api_token = self.api_token )
        self.test_secret_prefix = 'TEST_SECRET_'
        self.test_secret_name   = f'{self.test_secret_prefix}{random_string(8).upper()}'

    def tearDown(self):                                                          # Clean up test secrets
        # Clean up any test secrets created during tests
        existing_secrets = self.github_secrets.list_secrets()
        for secret in existing_secrets:
            if secret['name'].startswith(self.test_secret_prefix):
                try:
                    self.github_secrets.delete_secret(secret['name'])
                except Exception:
                    pass  # Ignore cleanup errors

    def test__init__(self):                                                      # Test basic initialization
        assert type(self.github_secrets)      is GitHub__Secrets
        assert self.github_secrets.api_token  == self.api_token
        assert self.github_secrets.repo_name  == self.test_repo
        assert self.github_secrets.owner      == self.test_repo_owner
        assert self.github_secrets.repo       == self.test_repo_name
        assert type(self.github_secrets.api)  is GitHub__API

    def test__init__invalid_repo_name(self):                                    # Test initialization with invalid repo name
        with self.assertRaises(ValueError) as context:
            GitHub__Secrets(repo_name = 'invalid-format' ,
                                   api_token = self.api_token   )

        assert "repo_name must be in format 'owner/repo'" in str(context.exception)

    def test__encrypt_secret(self):                                             # Test secret encryption
        public_key_data = self.github_secrets.get_public_key()
        secret_value    = 'test_secret_value_123'

        encrypted = self.github_secrets._encrypt_secret(public_key_data['key'] ,
                                                        secret_value           )

        assert type(encrypted)  is str
        assert len(encrypted)   > len(secret_value)
        assert encrypted        != secret_value

    def test_get_public_key(self):                                              # Test getting repository public key
        result = self.github_secrets.get_public_key()

        assert type(result)           is dict
        assert 'key_id'               in result
        assert 'key'                  in result
        assert type(result['key_id']) is str
        assert type(result['key'])    is str
        assert len(result['key'])     > 0

    def test_get_public_key__cached(self):                                      # Test that public key is cached
        # First call
        result1 = self.github_secrets.get_public_key()

        # Second call should return same cached result
        result2 = self.github_secrets.get_public_key()

        assert result1 == result2
        assert result1['key_id'] == result2['key_id']
        assert result1['key']    == result2['key']

    def test_list_secrets(self):                                                # Test listing repository secrets
        result = self.github_secrets.list_secrets()

        assert type(result) is list
        for secret in result:
            assert type(secret)         is dict
            assert 'name'               in secret
            assert 'created_at'         in secret
            assert 'updated_at'         in secret
            assert type(secret['name']) is str

    def test_get_secret__existing(self):                                        # Test getting existing secret metadata
        # First create a secret
        secret_value = 'test_value_for_get'
        self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                    secret_value          )

        # Now get its metadata
        result = self.github_secrets.get_secret(self.test_secret_name)

        assert type(result)              is dict
        assert result['name']            == self.test_secret_name
        assert 'created_at'              in result
        assert 'updated_at'              in result
        assert type(result['created_at']) is str
        assert type(result['updated_at']) is str

    def test_get_secret__nonexistent(self):                                     # Test getting nonexistent secret
        nonexistent_name = 'NONEXISTENT_SECRET_XYZ_12345'
        result = self.github_secrets.get_secret(nonexistent_name)

        assert result is None

    def test_create_or_update_secret__create(self):                             # Test creating a new secret
        secret_value = 'new_secret_value_123'

        result = self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                             secret_value          )

        assert result is True

        # Verify it was created
        secret_info = self.github_secrets.get_secret(self.test_secret_name)
        assert secret_info is not None
        assert secret_info['name'] == self.test_secret_name

    def test_create_or_update_secret__update(self):                             # Test updating an existing secret
        initial_value = 'initial_value'
        updated_value = 'updated_value'

        # Create secret
        result1 = self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                              initial_value         )
        assert result1 is True

        # Update secret
        result2 = self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                              updated_value         )
        assert result2 is True

        # Verify it still exists
        secret_info = self.github_secrets.get_secret(self.test_secret_name)
        assert secret_info is not None

    def test_create_or_update_secret__invalid_name(self):                       # Test creating secret with invalid name
        invalid_name = ''  # Empty name
        secret_value = 'test_value'

        result = self.github_secrets.create_or_update_secret(invalid_name ,
                                                             secret_value )

        assert result is False

    def test_delete_secret__existing(self):                                     # Test deleting existing secret
        # First create a secret
        secret_value = 'value_to_delete'
        self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                    secret_value          )

        # Verify it exists
        assert self.github_secrets.secret_exists(self.test_secret_name) is True

        # Delete it
        result = self.github_secrets.delete_secret(self.test_secret_name)
        assert result is True

        # Verify it's gone
        assert self.github_secrets.secret_exists(self.test_secret_name) is False

    def test_delete_secret__nonexistent(self):                                  # Test deleting nonexistent secret
        nonexistent_name = 'NONEXISTENT_SECRET_TO_DELETE_XYZ'

        result = self.github_secrets.delete_secret(nonexistent_name)

        assert result is False

    def test_configure_secrets__basic(self):                                    # Test configuring multiple secrets
        secrets = { f'{self.test_secret_prefix}ONE'   : 'value_one'   ,
                   f'{self.test_secret_prefix}TWO'   : 'value_two'   ,
                   f'{self.test_secret_prefix}THREE' : 'value_three' }

        results = self.github_secrets.configure_secrets(secrets)

        assert type(results) is dict
        assert results[f'set_{self.test_secret_prefix}ONE']   is True
        assert results[f'set_{self.test_secret_prefix}TWO']   is True
        assert results[f'set_{self.test_secret_prefix}THREE'] is True

        # Verify all were created
        for secret_name in secrets.keys():
            assert self.github_secrets.secret_exists(secret_name) is True

    @pytest.mark.skip("this works but the replace_all=True has the side effect of removing the secrets (which we need at the moment to stay there)")
    def test_configure_secrets__replace_all(self):                              # Test replace_all functionality
        # Create initial secrets
        initial_secrets = { f'{self.test_secret_prefix}KEEP'   : 'keep_value'   ,
                           f'{self.test_secret_prefix}DELETE' : 'delete_value' }

        self.github_secrets.configure_secrets(initial_secrets)

        # Configure with replace_all=True
        new_secrets = { f'{self.test_secret_prefix}KEEP' : 'keep_value_updated' ,
                       f'{self.test_secret_prefix}NEW'  : 'new_value'          }

        results = self.github_secrets.configure_secrets(new_secrets    ,
                                                        replace_all = True )

        assert results[f'set_{self.test_secret_prefix}KEEP']      is True
        assert results[f'set_{self.test_secret_prefix}NEW']       is True
        assert results[f'delete_{self.test_secret_prefix}DELETE'] is True

        # Verify final state
        assert self.github_secrets.secret_exists(f'{self.test_secret_prefix}KEEP')   is True
        assert self.github_secrets.secret_exists(f'{self.test_secret_prefix}NEW')    is True
        assert self.github_secrets.secret_exists(f'{self.test_secret_prefix}DELETE') is False

    def test_secret_exists__true(self):                                         # Test secret_exists for existing secret
        # Create a secret
        self.github_secrets.create_or_update_secret(self.test_secret_name ,
                                                    'test_value'          )

        result = self.github_secrets.secret_exists(self.test_secret_name)

        assert result is True

    def test_secret_exists__false(self):                                        # Test secret_exists for nonexistent secret
        nonexistent_name = 'DEFINITELY_DOES_NOT_EXIST_XYZ_789'

        result = self.github_secrets.secret_exists(nonexistent_name)

        assert result is False

    def test_configure_from_env_vars__with_values(self):                        # Test configuring from environment variables
        import os

        # Set up test environment variables
        test_env_var_1 = 'TEST_ENV_VAR_ONE'
        test_env_var_2 = 'TEST_ENV_VAR_TWO'
        os.environ[test_env_var_1] = 'env_value_one'
        os.environ[test_env_var_2] = 'env_value_two'

        env_mapping = { f'{self.test_secret_prefix}ENV_ONE' : test_env_var_1 ,
                       f'{self.test_secret_prefix}ENV_TWO' : test_env_var_2 }

        results = self.github_secrets.configure_from_env_vars(env_mapping)

        assert results[f'set_{self.test_secret_prefix}ENV_ONE'] is True
        assert results[f'set_{self.test_secret_prefix}ENV_TWO'] is True

        # Clean up env vars
        del os.environ[test_env_var_1]
        del os.environ[test_env_var_2]

    def test_configure_from_env_vars__missing_values(self):                     # Test configuring with missing env vars
        env_mapping = { f'{self.test_secret_prefix}MISSING' : 'NONEXISTENT_ENV_VAR_XYZ' }

        results = self.github_secrets.configure_from_env_vars(env_mapping)

        assert results[f'skip_{self.test_secret_prefix}MISSING'] is False

    # def test_list_org_secrets(self):                                           # Test listing organization secrets
    #     org_name = self.test_repo_owner
    #
    #     try:
    #         results = self.github_secrets.list_org_secrets(org_name)
    #
    #         assert type(results) is list
    #         for secret in results:
    #             assert type(secret)           is dict
    #             assert 'name'                 in secret
    #             assert 'created_at'           in secret
    #             assert 'updated_at'           in secret
    #             assert 'visibility'           in secret
    #             assert 'selected_repositories_url' in secret
    #     except HTTPError as e:
    #         if '403' in str(e) or '404' in str(e):
    #             self.skipTest('No org admin access or not an organization')
    #         else:
    #             raise

    # def test_create_or_update_org_secret(self):                                # Test creating organization secret
    #     org_name     = self.test_repo_owner
    #     secret_name  = f'{self.test_secret_prefix}ORG_{random_string(6).upper()}'
    #     secret_value = 'org_secret_value'
    #
    #     try:
    #         result = self.github_secrets.create_or_update_org_secret(org_name     ,
    #                                                                  secret_name  ,
    #                                                                  secret_value ,
    #                                                                  visibility = 'private' )
    #
    #         assert result is True
    #
    #         # Try to clean up
    #         try:
    #             endpoint = f"/orgs/{org_name}/actions/secrets/{secret_name}"
    #             self.github_secrets.api.delete(endpoint)
    #         except:
    #             pass
    #
    #     except HTTPError as e:
    #         if '403' in str(e) or '404' in str(e):
    #             self.skipTest('No org admin access or not an organization')
    #         else:
    #             raise

    def test_list_environment_secrets(self):                                    # Test listing environment secrets
        environment = 'production'  # Common environment name

        try:
            results = self.github_secrets.list_environment_secrets(environment)

            assert type(results) is list
            for secret in results:
                assert type(secret)  is dict
                assert 'name'        in secret
                assert 'created_at'  in secret
                assert 'updated_at'  in secret

        except HTTPError as e:
            if '404' in str(e):
                self.skipTest('Environment not found in repository')
            else:
                raise

    # def test_create_or_update_environment_secret(self):                         # Test creating environment secret
    #     environment  = 'production'  # Needs to exist in the repo
    #     secret_name  = f'{self.test_secret_prefix}ENV_{random_string(6).upper()}'
    #     secret_value = 'env_secret_value'
    #
    #     try:
    #         result = self.github_secrets.create_or_update_environment_secret(environment  ,
    #                                                                         secret_name  ,
    #                                                                         secret_value )
    #
    #         assert result is True
    #
    #         # Try to clean up
    #         try:
    #             endpoint = f"/repos/{self.github_secrets.owner}/{self.github_secrets.repo}/environments/{environment}/secrets/{secret_name}"
    #             self.github_secrets.api.delete(endpoint)
    #         except:
    #             pass
    #
    #     except HTTPError as e:
    #         if '404' in str(e):
    #             self.skipTest('Environment not found in repository')
    #         else:
    #             raise