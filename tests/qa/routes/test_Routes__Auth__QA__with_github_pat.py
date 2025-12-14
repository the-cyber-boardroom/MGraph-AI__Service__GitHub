from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client, skip_if_no_github_pat


class test_Routes__Auth__QA__with_github_pat(TestCase):                             # QA tests requiring a valid GitHub PAT

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        with setup__qa_test_objs() as _:
            cls.http_client    = _.http_client
            cls.github_pat     = str(_.http_client.github_pat)
            cls.encrypted_pat  = None                                               # Will be set after token-create

    def test_1__token_create(self):                                                 # POST /auth/token-create - Create encrypted token from PAT
        with self.http_client as _:
            headers  = {'X-GitHub-PAT': self.github_pat}
            response = _.post('/auth/token-create', headers=headers)
            result   = response.json()

            assert response.status_code == 200

            if result.get('success'):
                assert result.get('encrypted_pat')  is not None
                assert result.get('user')           is not None
                assert result.get('instructions')   is not None

                user = result.get('user')
                assert user.get('login') is not None                                # GitHub username
                assert user.get('id')    is not None                                # GitHub user ID

                test_Routes__Auth__QA__with_github_pat.encrypted_pat = result.get('encrypted_pat')
            else:
                # PAT might be invalid or have issues
                assert result.get('error')      is not None
                assert result.get('error_type') is not None

    def test_2__token_validate(self):                                               # POST /auth/token-validate - Validate encrypted token
        if not self.encrypted_pat:
            self.skipTest("No encrypted PAT available - token-create may have failed")

        with self.http_client as _:
            headers  = {'X-OSBot-GitHub-PAT': self.encrypted_pat}
            response = _.post('/auth/token-validate', headers=headers)
            result   = response.json()

            assert response.status_code == 200

            if result.get('success'):
                assert result.get('user')       is not None
                assert result.get('rate_limit') is not None

                rate_limit = result.get('rate_limit')
                assert rate_limit.get('limit')     is not None                      # e.g., 5000
                assert rate_limit.get('remaining') is not None
            else:
                # Token might have expired or decryption failed
                assert result.get('error')      is not None
                assert result.get('error_type') is not None

    def test_3__test_endpoint(self):                                                # GET /auth/test - Test encrypted PAT with GitHub API
        if not self.encrypted_pat:
            self.skipTest("No encrypted PAT available - token-create may have failed")

        with self.http_client as _:
            headers  = {'X-OSBot-GitHub-PAT': self.encrypted_pat}
            response = _.get('/auth/test', headers=headers)
            result   = response.json()

            assert response.status_code == 200

            if result.get('success'):
                assert result.get('user')       is not None
                assert result.get('rate_limit') is not None

                user = result.get('user')
                assert user.get('login')       is not None
                assert user.get('id')          is not None
                assert user.get('public_repos') is not None or user.get('public_repos') == 0
            else:
                assert result.get('error')      is not None
                assert result.get('error_type') is not None
