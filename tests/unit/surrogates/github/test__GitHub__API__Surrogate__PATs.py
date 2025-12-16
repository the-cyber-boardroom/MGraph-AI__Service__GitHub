from unittest                                                                       import TestCase
from osbot_utils.decorators.methods.cache_on_self                                   import cache_on_self
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate__PATs        import GitHub__API__Surrogate__PATs


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