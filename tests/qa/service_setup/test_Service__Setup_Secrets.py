import pytest
from unittest                                                         import TestCase
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List
from osbot_utils.utils.Env                                            import get_env
from tests.qa.service_setup.Service__Setup_Secrets                    import Service__Setup_Secrets
from mgraph_ai_service_github.service.github.GitHub__Secrets          import GitHub__Secrets

from osbot_utils.utils.Dev import pprint

class test_Service__Setup_Secrets(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_secrets = Service__Setup_Secrets()
        if cls.setup_secrets.setup() is False:
            pytest.skip("skipping tests because setup secrets failed (are the .setup-secrets.env defined?")


    # ═══════════════════════════════════════════════════════════════════════════════
    # support methods
    # ═══════════════════════════════════════════════════════════════════════════════


    def test_github_secrets(self):
        with self.setup_secrets.github_secrets() as _:
            assert type(_) is GitHub__Secrets

    def test_repo(self):
        with self.setup_secrets as _:
            repo_name  = get_env('SERVICE__SETUP__SECRETS__REPO_NAME' )
            repo_owner = get_env('SERVICE__SETUP__SECRETS__REPO_OWNER')
            assert _.repo() == f'{repo_owner}/{repo_name}'

    def test_setup(self):                                                              # Initialize test fixtures
        with self.setup_secrets as _:
            assert _.setup() is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # main methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_current_secrets(self):
        secrets = self.setup_secrets.current_secrets()
        assert type(secrets) is Type_Safe__List

    def test_secrets_to_configure(self):
        with self.setup_secrets.secrets_to_configure() as _:
            assert type(_) is GitHub__Secrets


