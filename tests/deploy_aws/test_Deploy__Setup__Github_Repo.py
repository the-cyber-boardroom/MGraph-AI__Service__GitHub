from unittest                                                   import TestCase
from osbot_utils.utils.Env                                      import load_dotenv
from mgraph_ai_service_github.config                            import ENV_VAR__GIT_HUB__ACCESS_TOKEN
from mgraph_ai_service_github.service.github.GitHub__Secrets    import GitHub__Secrets
from mgraph_ai_service_github.utils.deploy.Setup__GitHub__Repo  import Setup__GitHub__Repo


class test_Setup__GitHub__Repo(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.setup_github_repo = Setup__GitHub__Repo()

    def test__setUpClass(self):
        with self.setup_github_repo as _:
            assert type(_)                == Setup__GitHub__Repo
            assert type(_.github_secrets) is GitHub__Secrets

    def test_gh_access_token__name(self):
        with self.setup_github_repo as _:
            assert _.gh_access_token__name() == ENV_VAR__GIT_HUB__ACCESS_TOKEN

    def test_gh_access_token__update(self):
        with self.setup_github_repo as _:
            assert _.gh_access_token__update() is True
            assert _.gh_access_token__exists() is True