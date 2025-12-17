from unittest                                                                            import TestCase
from mgraph_ai_service_github.surrogates.github.schemas.Enum__GitHub__Scope              import Enum__GitHub__Scope
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__PAT           import Schema__Surrogate__PAT


class test__Schema__Surrogate__PAT(TestCase):

    def test_has_any_scope(self):
        pat = Schema__Surrogate__PAT(token      = "test_token"                           ,
                                     user_login = "test_user"                            ,
                                     user_id    = 123                                    ,
                                     scopes     = [Enum__GitHub__Scope.REPO]             )

        # Has matching scope
        assert pat.has_any_scope([Enum__GitHub__Scope.REPO, Enum__GitHub__Scope.WORKFLOW]) is True

        # No matching scope
        assert pat.has_any_scope([Enum__GitHub__Scope.ADMIN_ORG]) is False

        # Empty list
        assert pat.has_any_scope([]) is False


