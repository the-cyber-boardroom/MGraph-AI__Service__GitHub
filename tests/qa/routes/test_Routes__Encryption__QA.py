from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client, skip_if_no_github_pat


class test_Routes__Encryption__QA(TestCase):                                        # QA tests for /encryption/* routes against live server

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client

    def test__setUpClass(self):                                                     # Verify test setup completed correctly
        with self.http_client as _:
            assert type(_) is QA__HTTP_Client

    def test_public_key(self):                                                      # GET /encryption/public-key - Get server's public key
        with self.http_client as _:
            response = _.get('/encryption/public-key')
            result   = response.json()

            assert response.status_code     == 200
            assert result.get('public_key') is not None
            assert result.get('algorithm')  == 'NaCl/Curve25519/SealedBox'
            assert result.get('timestamp')  is not None

            public_key = result.get('public_key')
            assert len(public_key) == 64                                            # 32 bytes as hex = 64 chars
            assert all(c in '0123456789abcdef' for c in public_key)                 # Valid lowercase hex

    def test_generate_keys(self):                                                   # GET /encryption/generate-keys - Generate new key pair
        with self.http_client as _:
            response = _.get('/encryption/generate-keys')
            result   = response.json()

            assert response.status_code      == 200
            assert result.get('success')     is True
            assert result.get('public_key')  is not None
            assert result.get('private_key') is not None
            assert result.get('timestamp')   is not None

            public_key  = result.get('public_key')
            private_key = result.get('private_key')

            assert len(public_key)  == 64                                           # 32 bytes as hex
            assert len(private_key) == 64                                           # 32 bytes as hex
            assert public_key       != private_key                                  # Keys must be different

    def test_generate_keys__unique_each_call(self):                                 # Verify generate-keys returns different keys each time
        with self.http_client as _:
            response_1 = _.get('/encryption/generate-keys')
            response_2 = _.get('/encryption/generate-keys')

            result_1 = response_1.json()
            result_2 = response_2.json()

            assert result_1.get('public_key')  != result_2.get('public_key')
            assert result_1.get('private_key') != result_2.get('private_key')