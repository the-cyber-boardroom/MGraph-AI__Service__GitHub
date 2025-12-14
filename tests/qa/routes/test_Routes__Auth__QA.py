from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client


class test_Routes__Auth__QA(TestCase):                                              # QA tests for /auth/* routes against live server

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client
            cls.github_pat  = _.http_client.github_pat

    def test__setUpClass(self):                                                     # Verify test setup completed correctly
        with self.http_client as _:
            assert type(_) is QA__HTTP_Client

    def test_public_key(self):                                                      # GET /auth/public-key - Get server's public key for encryption
        with self.http_client as _:
            response = _.get('/auth/public-key')
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('public_key') is not None
            assert result.get('algorithm')  == 'NaCl/Curve25519/SealedBox'
            assert result.get('timestamp')  is not None

            public_key = result.get('public_key')
            assert len(public_key) == 64                                            # 32 bytes as hex = 64 chars
            assert all(c in '0123456789abcdef' for c in public_key)                 # Valid lowercase hex

    def test_test_api_key(self):                                                    # GET /auth/test-api-key - Verify service is running
        with self.http_client as _:
            response = _.get('/auth/test-api-key')
            result   = response.json()

            assert response.status_code           == 200
            assert result.get('success')          is True
            assert result.get('service')          == 'mgraph_ai_service_github'
            assert result.get('version')          is not None
            assert result.get('auth_configured')  in [True, False]                  # Depends on key config
            assert result.get('message')          == 'Service API key is valid'