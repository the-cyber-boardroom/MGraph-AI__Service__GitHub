import json
import base64
from unittest                                                               import TestCase
from osbot_utils.utils.Env                                                  import env_var_set
from starlette.testclient                                                   import TestClient
from mgraph_ai_service_github.config                                        import ENV_VAR__SERVICE__AUTH__PUBLIC_KEY, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY
from mgraph_ai_service_github.fast_api.GitHub__Service__Fast_API            import GitHub__Service__Fast_API
from mgraph_ai_service_github.schemas.encryption.Const__Encryption          import NCCL__ALGORITHM
from tests.unit.GitHub__Service__Fast_API__Test_Objs                        import setup__github_service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE, GitHub__Service__Fast_API__Test_Objs


class test_Routes__Encryption__client(TestCase):

    @classmethod
    def setUpClass(cls):
        with setup__github_service_fast_api_test_objs() as _:
            cls.test_objs      = _
            cls.github_service = _.fast_api
            cls.client         = _.fast_api__client
            cls.nacl_keys      = _.nacl_keys
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

        cls.test_text      = "Hello, World! This is a test message."
        cls.test_json_dict = {"name": "Test User", "id": 12345, "active": True}
        cls.test_json_str  = json.dumps(cls.test_json_dict, separators=(',', ':'))
        cls.test_binary    = b"Binary test data \x00\x01\x02\x03"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Verification Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_setUpClass(self):                                                                  # Verify test setup is correct
        with self.test_objs as _:
            assert type(_) is GitHub__Service__Fast_API__Test_Objs

        with self.github_service as _:
            assert type(_) is GitHub__Service__Fast_API

        with self.client as _:
            assert type(_) is TestClient

        assert env_var_set(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY ) is True
        assert env_var_set(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY) is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /encryption/public-key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption_public_key(self):                                                      # Test GET /encryption/public-key returns public key
        response = self.client.get('/encryption/public-key')
        result   = response.json()

        assert response.status_code     == 200
        assert result.get('algorithm')  == NCCL__ALGORITHM
        assert result.get('timestamp')  is not None

        public_key = result.get('public_key')
        assert public_key                                       is not None                     # Key must be configured
        assert len(public_key)                                  == 64                           # 32 bytes as hex
        assert all(c in '0123456789abcdef' for c in public_key)                                 # Valid lowercase hex
        assert public_key                                       == self.nacl_keys.public_key    # Should match what we set

    # ═══════════════════════════════════════════════════════════════════════════════
    # GET /encryption/generate-keys Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption_generate_keys(self):                                                   # Test GET /encryption/generate-keys returns new key pair
        response = self.client.get('/encryption/generate-keys')
        result   = response.json()

        assert response.status_code       == 200
        assert result.get('success')      is True
        assert result.get('public_key')   is not None
        assert result.get('private_key')  is not None
        assert result.get('timestamp')    is not None

        public_key  = result.get('public_key')
        private_key = result.get('private_key')

        assert len(public_key)   == 64
        assert len(private_key)  == 64
        assert public_key        != private_key

    def test__encryption_generate_keys__unique(self):                                           # Test each call generates unique keys
        response_1 = self.client.get('/encryption/generate-keys')
        response_2 = self.client.get('/encryption/generate-keys')

        result_1 = response_1.json()
        result_2 = response_2.json()

        assert result_1.get('public_key')  != result_2.get('public_key')
        assert result_1.get('private_key') != result_2.get('private_key')

    # ═══════════════════════════════════════════════════════════════════════════════
    # POST /encryption/encrypt Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption_encrypt__text(self):                                                   # Test POST /encryption/encrypt with text
        request_data = {'value': self.test_text, 'encryption_type': 'text'}
        response     = self.client.post('/encryption/encrypt', json=request_data)
        result       = response.json()

        assert response.status_code     == 200
        assert result.get('success')    is True
        assert result.get('encrypted')  is not None
        assert result.get('algorithm')  == NCCL__ALGORITHM
        assert result.get('timestamp')  is not None

        encrypted = result.get('encrypted')
        decoded   = base64.b64decode(encrypted)                                                 # Verify valid base64
        assert len(decoded) > len(self.test_text)                                               # Encrypted has overhead

    def test__encryption_encrypt__json(self):                                                   # Test POST /encryption/encrypt with JSON
        request_data = {'value': self.test_json_str, 'encryption_type': 'json'}
        response     = self.client.post('/encryption/encrypt', json=request_data)
        result       = response.json()

        assert response.status_code    == 200
        assert result.get('success')   is True
        assert result.get('encrypted') is not None

    def test__encryption_encrypt__json_invalid(self):                                           # Test POST /encryption/encrypt with invalid JSON
        request_data = {'value': 'not valid json {]', 'encryption_type': 'json'}
        response     = self.client.post('/encryption/encrypt', json=request_data)
        result       = response.json()

        assert response.status_code    == 200
        assert result.get('success')   is False
        assert result.get('error')     is not None
        assert result.get('encrypted') is None

    def test__encryption_encrypt__data(self):                                                   # Test POST /encryption/encrypt with binary data
        data_b64     = base64.b64encode(self.test_binary).decode('utf-8')
        request_data = {'value': data_b64, 'encryption_type': 'data'}
        response     = self.client.post('/encryption/encrypt', json=request_data)
        result       = response.json()

        assert response.status_code    == 200
        assert result.get('success')   is True
        assert result.get('encrypted') is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # POST /encryption/decrypt Tests - Round Trips
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption_decrypt__text_round_trip(self):                                        # Test encrypt -> decrypt round trip for text
        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : self.test_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        assert encrypt_result.get('success') is True
        encrypted = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'text'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_response.status_code == 200
        assert decrypt_result.get('success')   is True
        assert decrypt_result.get('decrypted') == self.test_text

    def test__encryption_decrypt__json_round_trip(self):                                        # Test encrypt -> decrypt round trip for JSON
        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : self.test_json_str,
            'encryption_type': 'json'
        })
        encrypt_result = encrypt_response.json()
        assert encrypt_result.get('success') is True
        encrypted = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'json'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_response.status_code == 200
        assert decrypt_result.get('success') is True
        decrypted_dict = json.loads(decrypt_result.get('decrypted'))
        assert decrypted_dict == self.test_json_dict

    def test__encryption_decrypt__data_round_trip(self):                                        # Test encrypt -> decrypt round trip for binary data
        data_b64 = base64.b64encode(self.test_binary).decode('utf-8')

        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : data_b64,
            'encryption_type': 'data'
        })
        encrypt_result = encrypt_response.json()
        assert encrypt_result.get('success') is True
        encrypted = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'data'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_response.status_code == 200
        assert decrypt_result.get('success') is True
        decrypted_binary = base64.b64decode(decrypt_result.get('decrypted'))
        assert decrypted_binary == self.test_binary

    def test__encryption_decrypt__wrong_type(self):                                             # Test decrypt with wrong type fails
        # Encrypt as TEXT
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : self.test_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        encrypted      = encrypt_result.get('encrypted')

        # Try to decrypt as JSON (wrong type)
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'json'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_response.status_code == 200
        assert decrypt_result.get('success')   is False
        assert decrypt_result.get('decrypted') is None

    def test__encryption_decrypt__invalid_encrypted_data(self):                                 # Test decrypt with invalid encrypted data
        fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')

        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : fake_encrypted,
            'encryption_type': 'text'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_response.status_code == 200
        assert decrypt_result.get('success')   is False
        assert decrypt_result.get('decrypted') is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # POST /encryption/validate Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption_validate__valid(self):                                                 # Test POST /encryption/validate with decryptable data
        # First encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : self.test_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        encrypted      = encrypt_result.get('encrypted')

        # Validate
        validate_response = self.client.post('/encryption/validate', json={
            'encrypted'      : encrypted,
            'encryption_type': 'text'
        })
        validate_result = validate_response.json()

        assert validate_response.status_code   == 200
        assert validate_result.get('success')     is True
        assert validate_result.get('can_decrypt') is True
        assert validate_result.get('duration')    >  0
        assert validate_result.get('size_bytes')  == len(self.test_text.encode('utf-8'))
        assert validate_result.get('error')       is None
        assert validate_result.get('timestamp')   is not None

    def test__encryption_validate__invalid(self):                                               # Test POST /encryption/validate with invalid data
        fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')

        validate_response = self.client.post('/encryption/validate', json={
            'encrypted'      : fake_encrypted,
            'encryption_type': 'text'
        })
        validate_result = validate_response.json()

        assert validate_response.status_code      == 200
        assert validate_result.get('success')     is False
        assert validate_result.get('can_decrypt') is False
        assert validate_result.get('error')       is not None

    def test__encryption_validate__wrong_type(self):                                            # Test POST /encryption/validate with wrong expected type
        # Encrypt as TEXT
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : self.test_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        encrypted      = encrypt_result.get('encrypted')

        # Validate as JSON (wrong type)
        validate_response = self.client.post('/encryption/validate', json={
            'encrypted'      : encrypted,
            'encryption_type': 'json'
        })
        validate_result = validate_response.json()

        assert validate_response.status_code      == 200
        assert validate_result.get('success')     is False
        assert validate_result.get('can_decrypt') is False
        assert validate_result.get('error')       is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Unicode and Special Characters Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption__unicode_round_trip(self):                                             # Test encrypt/decrypt with unicode characters
        unicode_text = "Hello 世界! 🔐🔑 مرحبا"

        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : unicode_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        encrypted      = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'text'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_result.get('success')   is True
        assert decrypt_result.get('decrypted') == unicode_text

    def test__encryption__special_chars_round_trip(self):                                       # Test encrypt/decrypt with special characters
        special_text = "Special: !@#$%^&*(){}[]|\\:;\"'<>?,./\n\t"

        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : special_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        encrypted      = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'text'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_result.get('success')   is True
        assert decrypt_result.get('decrypted') == special_text

    def test__encryption__large_text_round_trip(self):                                          # Test encrypt/decrypt with larger text
        large_text = "A" * 10000                                                                # 10KB of text

        # Encrypt
        encrypt_response = self.client.post('/encryption/encrypt', json={
            'value'          : large_text,
            'encryption_type': 'text'
        })
        encrypt_result = encrypt_response.json()
        assert encrypt_result.get('success') is True
        encrypted = encrypt_result.get('encrypted')

        # Decrypt
        decrypt_response = self.client.post('/encryption/decrypt', json={
            'encrypted'      : encrypted,
            'encryption_type': 'text'
        })
        decrypt_result = decrypt_response.json()

        assert decrypt_result.get('success')   is True
        assert decrypt_result.get('decrypted') == large_text

    # ═══════════════════════════════════════════════════════════════════════════════
    # Authentication Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encryption__no_api_key__get(self):                                                # Test GET routes require API key
        with setup__github_service_fast_api_test_objs() as _:
            client_no_auth = TestClient(_.fast_api__app)

        response = client_no_auth.get('/encryption/public-key')

        assert response.status_code == 401
        result = response.json()
        assert result.get('status')  == 'error'
        assert 'API key'             in result.get('message', '')

    def test__encryption__no_api_key__post(self):                                               # Test POST routes require API key
        with setup__github_service_fast_api_test_objs() as _:
            client_no_auth = TestClient(_.fast_api__app)

        response = client_no_auth.post('/encryption/encrypt', json={
            'value'          : 'test',
            'encryption_type': 'text'
        })

        assert response.status_code == 401