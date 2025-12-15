import base64
import json
from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs


class test_Routes__Encryption__QA__encrypt_decrypt(TestCase):                       # QA tests for encryption/decryption round-trips

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client

        cls.test_text      = "Hello, World! This is a test message."
        cls.test_json      = {"name": "Test User", "id": 12345, "active": True}
        cls.test_binary    = b"Binary test data \x00\x01\x02\x03"

    def test_encrypt_text(self):                                                    # POST /encryption/encrypt - Encrypt text
        with self.http_client as _:
            request_data = {'value'          : self.test_text ,
                            'encryption_type': 'text'         }
            response     = _.post('/encryption/encrypt', json=request_data)
            result       = response.json()

            assert response.status_code     == 200
            assert result.get('success')    is True
            assert result.get('encrypted')  is not None
            assert result.get('algorithm')  == 'NaCl/Curve25519/SealedBox'
            assert result.get('timestamp')  is not None

            encrypted = result.get('encrypted')
            base64.b64decode(encrypted)                                             # Should be valid base64

    def test_encrypt_json(self):                                                    # POST /encryption/encrypt - Encrypt JSON
        with self.http_client as _:
            json_str     = json.dumps(self.test_json, separators=(',', ':'))
            request_data = {'value'          : json_str ,
                            'encryption_type': 'json'   }
            response     = _.post('/encryption/encrypt', json=request_data)
            result       = response.json()

            assert response.status_code    == 200
            assert result.get('success')   is True
            assert result.get('encrypted') is not None

    def test_encrypt_data(self):                                                    # POST /encryption/encrypt - Encrypt binary data (base64)
        with self.http_client as _:
            data_b64     = base64.b64encode(self.test_binary).decode('utf-8')
            request_data = {'value'          : data_b64 ,
                            'encryption_type': 'data'   }
            response     = _.post('/encryption/encrypt', json=request_data)
            result       = response.json()

            assert response.status_code    == 200
            assert result.get('success')   is True
            assert result.get('encrypted') is not None

    def test_encrypt_decrypt__text_round_trip(self):                                # Full encrypt -> decrypt cycle for text
        with self.http_client as _:
            # Encrypt
            encrypt_request  = {'value': self.test_text, 'encryption_type': 'text'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Decrypt
            decrypt_request  = {'encrypted': encrypted, 'encryption_type': 'text'}
            decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
            decrypt_result   = decrypt_response.json()

            assert decrypt_result.get('success')   is True
            assert decrypt_result.get('decrypted') == self.test_text

    def test_encrypt_decrypt__json_round_trip(self):                                # Full encrypt -> decrypt cycle for JSON
        with self.http_client as _:
            json_str = json.dumps(self.test_json, separators=(',', ':'))

            # Encrypt
            encrypt_request  = {'value': json_str, 'encryption_type': 'json'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Decrypt
            decrypt_request  = {'encrypted': encrypted, 'encryption_type': 'json'}
            decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
            decrypt_result   = decrypt_response.json()

            assert decrypt_result.get('success')   is True
            decrypted_json = json.loads(decrypt_result.get('decrypted'))
            assert decrypted_json == self.test_json

    def test_encrypt_decrypt__data_round_trip(self):                                # Full encrypt -> decrypt cycle for binary data
        with self.http_client as _:
            data_b64 = base64.b64encode(self.test_binary).decode('utf-8')

            # Encrypt
            encrypt_request  = {'value': data_b64, 'encryption_type': 'data'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Decrypt
            decrypt_request  = {'encrypted': encrypted, 'encryption_type': 'data'}
            decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
            decrypt_result   = decrypt_response.json()

            assert decrypt_result.get('success') is True
            decrypted_binary = base64.b64decode(decrypt_result.get('decrypted'))
            assert decrypted_binary == self.test_binary

    def test_encrypt_decrypt__unicode(self):                                        # Unicode and emoji support
        with self.http_client as _:
            unicode_text = "Hello 世界! 🔐🔑 مرحبا"

            # Encrypt
            encrypt_request  = {'value': unicode_text, 'encryption_type': 'text'}
            encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
            encrypt_result   = encrypt_response.json()

            assert encrypt_result.get('success') is True
            encrypted = encrypt_result.get('encrypted')

            # Decrypt
            decrypt_request  = {'encrypted': encrypted, 'encryption_type': 'text'}
            decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
            decrypt_result   = decrypt_response.json()

            assert decrypt_result.get('success')   is True
            assert decrypt_result.get('decrypted') == unicode_text
