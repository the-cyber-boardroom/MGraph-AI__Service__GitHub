from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs        import GitHub__API__Surrogate__PATs
from mgraph_ai_service_github.surrogates.github.schemas.Enum__GitHub__Scope         import Enum__GitHub__Scope


class test__GitHub__API__Surrogate__PATs(TestCase):

    @cache_on_self
    def pats(self):
        return GitHub__API__Surrogate__PATs().setup()

    def test_setup(self):
        pats = self.pats()
        assert pats.admin_pat()        == pats.PAT__ADMIN
        assert pats.repo_write_pat()   == pats.PAT__REPO_WRITE
        assert pats.repo_read_pat()    == pats.PAT__REPO_READ
        assert pats.org_admin_pat()    == pats.PAT__ORG_ADMIN
        assert pats.expired_pat()      == pats.PAT__EXPIRED
        assert pats.rate_limited_pat() == pats.PAT__RATE_LIMITED
        assert pats.invalid_pat()      == pats.PAT__INVALID

    def test_pat_validation(self):
        pats = self.pats()

        # Admin PAT should be valid
        assert pats.is_valid_pat(pats.admin_pat()) is True
        assert pats.is_expired(pats.admin_pat())   is False

        # Expired PAT should not be valid
        assert pats.is_valid_pat(pats.expired_pat()) is False
        assert pats.is_expired(pats.expired_pat())   is True

        # Invalid PAT
        assert pats.is_valid_pat(pats.invalid_pat()) is False

        # Rate limited
        assert pats.is_rate_limited(pats.rate_limited_pat()) is True

        # Unknown PAT
        assert pats.is_valid_pat("unknown_pat") is False

    def test_scope_checking(self):
        pats = self.pats()

        # Admin has repo scope
        assert pats.can_read_repo_secrets(pats.admin_pat())  is True
        assert pats.can_write_repo_secrets(pats.admin_pat()) is True
        assert pats.can_admin_org(pats.admin_pat())          is True

        # Repo write has repo scope
        assert pats.can_read_repo_secrets(pats.repo_write_pat())  is True
        assert pats.can_write_repo_secrets(pats.repo_write_pat()) is True
        assert pats.can_admin_org(pats.repo_write_pat())          is False

        # Repo read has only public_repo scope
        assert pats.can_read_repo_secrets(pats.repo_read_pat())  is True
        assert pats.can_write_repo_secrets(pats.repo_read_pat()) is False

        # No scopes PAT
        assert pats.can_read_repo_secrets(pats.no_scopes_pat())  is False
        assert pats.can_write_repo_secrets(pats.no_scopes_pat()) is False

    def test_user_association(self):
        pats = self.pats()
        user = pats.get_user(pats.admin_pat())

        assert user is not None
        assert user.login == 'surrogate-admin'
        assert user.id    == 1000001

    def test_has_scope(self):
        pats = self.pats()

        # Admin has REPO scope
        assert pats.has_scope(pats.admin_pat(), Enum__GitHub__Scope.REPO)      is True
        assert pats.has_scope(pats.admin_pat(), Enum__GitHub__Scope.ADMIN_ORG) is True

        # Repo read only has PUBLIC_REPO
        assert pats.has_scope(pats.repo_read_pat(), Enum__GitHub__Scope.PUBLIC_REPO) is True
        assert pats.has_scope(pats.repo_read_pat(), Enum__GitHub__Scope.REPO)        is False

        # Unknown PAT
        assert pats.has_scope("unknown_pat", Enum__GitHub__Scope.REPO) is False

    def test_is_known_pat(self):
        pats = self.pats()

        assert pats.is_known_pat(pats.admin_pat()) is True
        assert pats.is_known_pat("unknown_pat")    is False

    def test_can_read_org(self):
        pats = self.pats()

        # Org admin can read org
        assert pats.can_read_org(pats.org_admin_pat()) is True

        # Admin has admin:org scope
        assert pats.can_read_org(pats.admin_pat()) is True

        # Repo-only cannot read org
        assert pats.can_read_org(pats.repo_write_pat()) is False

    def test_can_read_org_unknown_pat(self):
        pats = self.pats()
        # Unknown PAT should return False
        assert pats.can_read_org("unknown_pat_12345") is False

    def test_env_only_pat(self):
        pats = self.pats()
        assert pats.env_only_pat() == pats.PAT__ENV_ONLY
