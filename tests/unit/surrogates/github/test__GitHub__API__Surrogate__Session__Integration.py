from unittest                                                                       import TestCase
from mgraph_ai_service_github.surrogates.github.GitHub__API__Surrogate              import GitHub__API__Surrogate


class test__GitHub__API__Surrogate__Session__Integration(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.surrogate = GitHub__API__Surrogate().setup()

    def test_with_surrogate(self):
        session  = self.surrogate.create_session(self.surrogate.pats.admin_pat())

        # Make request through session
        response = session.get("https://api.github.com/user")

        assert response.status_code == 200
        assert response.json()['login'] == 'surrogate-admin'

    def test_session_with_different_pats(self):
        pats = self.surrogate.pats

        # Admin session
        admin_session = self.surrogate.create_session(pats.admin_pat())
        response      = admin_session.get("/user")
        assert response.json()['login'] == 'surrogate-admin'

        # Repo write session
        repo_session = self.surrogate.create_session(pats.repo_write_pat())
        response     = repo_session.get("/user")
        assert response.json()['login'] == 'surrogate-repo-write'

        # Expired session
        expired_session = self.surrogate.create_session(pats.expired_pat())
        response        = expired_session.get("/user")
        assert response.status_code == 401