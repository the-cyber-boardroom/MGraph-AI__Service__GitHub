import base64
from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client, skip_if_no_github_pat


class test_Routes__Encryption__QA__validate(TestCase):                              # QA tests for /encryption/validate endpoint

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client

    def test_validate__valid_encrypted_data(self):                                  # POST /encryption/validate - Validate decryptable data
        with self.http_client as _:
            # First encrypt something
            encrypt_request  = {'value': 'Test validation', 'encryption_type': 'text'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Validate
            validate_request  = {'encrypted': encrypted, 'encryption_type': 'text'}
            validate_response = _.post('/encryption/validate', json=validate_request)
            validate_result   = validate_response.json()

            assert validate_result.get('success')     is True
            assert validate_result.get('can_decrypt') is True
            assert validate_result.get('duration')    >  0
            assert validate_result.get('size_bytes')  == len('Test validation'.encode('utf-8'))
            assert validate_result.get('error')       is None

    def test_validate__invalid_encrypted_data(self):                                # POST /encryption/validate - Validate corrupted data
        with self.http_client as _:
            # Use random base64 that isn't valid encrypted data
            # Need at least 48 bytes due to NaCl SealedBox overhead validation
            fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')

            validate_request  = {'encrypted': fake_encrypted, 'encryption_type': 'text'}
            validate_response = _.post('/encryption/validate', json=validate_request)
            validate_result   = validate_response.json()

            assert validate_result.get('success')     is False
            assert validate_result.get('can_decrypt') is False
            assert validate_result.get('error')       is not None


class test_Routes__Encryption__QA__error_cases(TestCase):                           # QA tests for encryption error handling

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client

    def test_encrypt__invalid_json(self):                                           # POST /encryption/encrypt with invalid JSON content
        with self.http_client as _:
            request_data = {'value'          : 'not valid json {]' ,
                            'encryption_type': 'json'              }
            response     = _.post('/encryption/encrypt', json=request_data)
            result       = response.json()

            assert response.status_code  == 200
            assert result.get('success') is False
            assert result.get('error')   is not None                                # JSON parsing error

    def test_decrypt__wrong_type(self):                                             # Decrypt with wrong type (encrypted as text, decrypt as json)
        with self.http_client as _:
            # Encrypt as text
            encrypt_request  = {'value': 'plain text not json', 'encryption_type': 'text'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Try to decrypt as JSON
            decrypt_request  = {'encrypted': encrypted, 'encryption_type': 'json'}
            decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
            decrypt_result   = decrypt_response.json()

            assert decrypt_result.get('success') is False                           # Should fail JSON parsing

    def test_decrypt__invalid_base64(self):                                         # POST /encryption/decrypt with invalid base64
        with self.http_client as _:
            request_data = {'encrypted'      : 'not-valid-base64!!!' ,
                            'encryption_type': 'text'                }
            response     = _.post('/encryption/decrypt', json=request_data)

            assert response.json().get('error') == 'Invalid base64 encoded encrypted data: Only base64 data is allowed'
            assert response.status_code == 500