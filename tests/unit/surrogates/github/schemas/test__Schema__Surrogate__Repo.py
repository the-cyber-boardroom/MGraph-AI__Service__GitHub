from unittest                                                                   import TestCase
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Repo import Schema__Surrogate__Repo


class test__Schema__Surrogate__Repo(TestCase):

    def test_repo_key(self):
        repo = Schema__Surrogate__Repo(owner        = "test-owner"            ,
                                       name         = "test-repo"             ,
                                       full_name    = "test-owner/test-repo"  ,
                                       environments = []                      )

        assert repo.repo_key() == "test-owner/test-repo"