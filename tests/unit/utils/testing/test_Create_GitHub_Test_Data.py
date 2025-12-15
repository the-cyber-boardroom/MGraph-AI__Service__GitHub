import pytest
from unittest                                                       import TestCase

from osbot_fast_api_serverless.utils.testing.skip_tests             import skip__if_not__in_github_actions
from osbot_utils.utils.Env                                          import load_dotenv
from mgraph_ai_service_github.service.github.GitHub__API            import GitHub__API
from mgraph_ai_service_github.service.github.GitHub__Secrets        import GitHub__Secrets
from mgraph_ai_service_github.utils.testing.Create_GitHub_Test_Data import Create_GitHub_Test_Data


class test_Create_GitHub_Test_Data(TestCase):

    @classmethod
    def setUpClass(cls):
        skip__if_not__in_github_actions()                           # only run this in GH Actions
        load_dotenv()
        with Create_GitHub_Test_Data() as _:
            cls.create_test_data  = _
            if _.setup__env_vars_defined_ok() is False:
                pytest.skip("Skipping test due to missing environment variables")

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup methods
    # ═══════════════════════════════════════════════════════════════════════════════


    def test_github_api(self):
        with self.create_test_data.github_api() as _:
            assert type(_) is GitHub__API
            assert _.api_token == self.create_test_data.api_token()

    def test_github_secrets(self):
        with self.create_test_data.github_secrets() as _:
            assert type(_) is GitHub__Secrets
            assert type(_.list_secrets()) is list
            assert type(_.secrets_names()) is list


    # ═══════════════════════════════════════════════════════════════════════════════
    # main methods
    # ═══════════════════════════════════════════════════════════════════════════════

    # def test_create_repo_secrets(self):
    #     with self.create_test_data as _:
    #         assert _.create_repo_secrets() is True
    #
    # def test_create_env_secrets(self):
    #     with self.create_test_data as _:
    #         assert _.create_env_secrets() is True
    #
    # def test_create_org_secrets(self):
    #     with self.create_test_data as _:
    #         assert _.create_org_secrets() is True

    def test_create_all(self):
        with self.create_test_data as _:
            assert _.create_all() == {'env_secrets' : True,
                                      'org_secrets' : True,
                                      'repo_secrets': True}

