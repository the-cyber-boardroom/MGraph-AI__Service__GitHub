from unittest                                                   import TestCase
from mgraph_ai_service_github.service.github.GitHub__API        import GitHub__API
from mgraph_ai_service_github.utils.deploy.Setup__GitHub__Repo  import Setup__GitHub__Repo


class test_Setup__GitHub__Repo(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.setup_github_repo = Setup__GitHub__Repo()

    def test__setUpClass(self):
        with self.setup_github_repo as _:
            assert type(_)            == Setup__GitHub__Repo
            assert type(_.github_api) is GitHub__API