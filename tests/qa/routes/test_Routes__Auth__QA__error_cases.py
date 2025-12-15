from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client, skip_if_no_github_pat


class test_Routes__Auth__QA__error_cases(TestCase):                                 # QA tests for auth error handling

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client

    def test_token_create__missing_header(self):                                    # POST /auth/token-create without PAT header
        with self.http_client as _:
            response = _.post('/auth/token-create')                                 # No X-GitHub-PAT header
            result   = response.json()

            assert response.status_code    == 200                                   # Returns 200 with error in body
            assert result.get('success')   is False
            assert result.get('error')     == 'Missing X-GitHub-PAT header'
            assert result.get('error_type') == 'MISSING_HEADER'

    def test_token_validate__missing_header(self):                                  # POST /auth/token-validate without encrypted PAT
        with self.http_client as _:
            response = _.post('/auth/token-validate')                               # No X-OSBot-GitHub-PAT header
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('success')    is False
            assert result.get('error')      == 'Missing X-OSBot-GitHub-PAT header'
            assert result.get('error_type') == 'MISSING_HEADER'

    def test_test__missing_header(self):                                            # GET /auth/test without encrypted PAT
        with self.http_client as _:
            response = _.get('/auth/test')                                          # No X-OSBot-GitHub-PAT header
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('success')    is False
            assert result.get('error')      == 'Missing X-OSBot-GitHub-PAT header'
            assert result.get('error_type') == 'MISSING_HEADER'

    def test_token_validate__invalid_encrypted_data(self):                          # POST /auth/token-validate with invalid encrypted data
        with self.http_client as _:
            headers  = {'X-OSBot-GitHub-PAT': 'not-valid-base64-encrypted-data'}
            response = _.post('/auth/token-validate', headers=headers)
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('success')    is False
            assert result.get('error_type') == 'DECRYPTION_FAILED'

    def test_token_create__invalid_pat(self):                                       # POST /auth/token-create with invalid PAT
        with self.http_client as _:
            headers  = {'X-GitHub-PAT': 'ghp_invalid_pat_that_will_fail'}
            response = _.post('/auth/token-create', headers=headers)
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('success')    is False
            assert result.get('error_type') in ['INVALID_PAT', 'GITHUB_ERROR']