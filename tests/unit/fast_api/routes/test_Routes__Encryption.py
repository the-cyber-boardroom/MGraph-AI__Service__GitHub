import json
import base64
from unittest                                                                                   import TestCase
from osbot_fast_api.api.routes.Fast_API__Routes                                                 import Fast_API__Routes
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_classes
from mgraph_ai_service_github.fast_api.routes.Routes__Encryption                                import Routes__Encryption, TAG__ROUTES_ENCRYPTION, ROUTES_PATHS__ENCRYPTION
from mgraph_ai_service_github.schemas.encryption.Const__Encryption                              import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type                          import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Decrypted_Value                      import Safe_Str__Decrypted_Value
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value                      import Safe_Str__Encrypted_Value
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Request                    import Schema__Decryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Response                   import Schema__Decryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Request          import Schema__Decryption__Validate__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Response         import Schema__Decryption__Validate__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Request                    import Schema__Encryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Response                   import Schema__Encryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Key_Generation__Response               import Schema__Key_Generation__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Public_Key__Response                   import Schema__Public_Key__Response
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management                           import NaCl__Key_Management
from mgraph_ai_service_github.service.encryption.Service__Encryption                            import Service__Encryption


class test_Routes__Encryption(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nacl_manager        = NaCl__Key_Management()
        cls.test_keys           = cls.nacl_manager.generate_nacl_keys()
        cls.service_encryption  = Service__Encryption(private_key_hex = cls.test_keys.private_key ,
                                                      public_key_hex  = cls.test_keys.public_key  )
        cls.routes_encryption   = Routes__Encryption(service_encryption = cls.service_encryption)

        cls.test_text      = "Hello, World! This is a test message."
        cls.test_json_dict = {"name": "Test User", "id": 12345, "active": True}
        cls.test_json_str  = json.dumps(cls.test_json_dict, separators=(',', ':'))
        cls.test_binary    = b"Binary test data \x00\x01\x02\x03"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                     # Test auto-initialization
        with self.routes_encryption as _:
            assert type(_)                   is Routes__Encryption
            assert base_classes(_)           == [Fast_API__Routes, Type_Safe, object]
            assert _.tag                     == TAG__ROUTES_ENCRYPTION
            assert type(_.service_encryption) is Service__Encryption

    def test__routes_paths(self):                                                               # Test route paths constant
        assert ROUTES_PATHS__ENCRYPTION == [ '/encryption/public-key'    ,
                                             '/encryption/generate-keys' ,
                                             '/encryption/encrypt'       ,
                                             '/encryption/decrypt'       ,
                                             '/encryption/validate'      ]
        assert len(ROUTES_PATHS__ENCRYPTION) == 5

    # ═══════════════════════════════════════════════════════════════════════════════
    # public_key Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__public_key(self):                                                                 # Test public_key returns correct response
        with self.routes_encryption as _:
            result = _.public_key()

            assert type(result)      is Schema__Public_Key__Response
            assert result.public_key == self.test_keys.public_key
            assert result.algorithm  == NCCL__ALGORITHM
            assert result.timestamp  is not None

    def test__public_key__key_format(self):                                                     # Test public key is valid hex format
        with self.routes_encryption as _:
            result     = _.public_key()
            public_key = str(result.public_key)

            assert len(public_key)                                  == 64                       # 32 bytes as hex
            assert all(c in '0123456789abcdef' for c in public_key)                             # Valid lowercase hex

    # ═══════════════════════════════════════════════════════════════════════════════
    # generate_keys Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__generate_keys(self):                                                              # Test generate_keys returns new key pair
        with self.routes_encryption as _:
            result = _.generate_keys()

            assert type(result)        is Schema__Key_Generation__Response
            assert result.success      is True
            assert result.public_key   is not None
            assert result.private_key  is not None
            assert result.timestamp    is not None

    def test__generate_keys__key_format(self):                                                  # Test generated keys are valid hex format
        with self.routes_encryption as _:
            result      = _.generate_keys()
            public_key  = str(result.public_key)
            private_key = str(result.private_key)

            assert len(public_key)   == 64                                                      # 32 bytes as hex
            assert len(private_key)  == 64
            assert public_key        != private_key                                             # Keys must be different

    def test__generate_keys__unique_each_call(self):                                            # Test each call generates unique keys
        with self.routes_encryption as _:
            result_1 = _.generate_keys()
            result_2 = _.generate_keys()

            assert result_1.public_key  != result_2.public_key
            assert result_1.private_key != result_2.private_key

    # ═══════════════════════════════════════════════════════════════════════════════
    # encrypt Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__encrypt__text(self):                                                              # Test encrypt with text type
        with self.routes_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                  encryption_type = Enum__Encryption_Type.TEXT                )
            result  = _.encrypt(request)

            assert type(result)       is Schema__Encryption__Response
            assert result.success     is True
            assert result.encrypted   is not None
            assert result.algorithm   == NCCL__ALGORITHM
            assert result.timestamp   is not None

    def test__encrypt__text__valid_base64(self):                                                # Test encrypted output is valid base64
        with self.routes_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                  encryption_type = Enum__Encryption_Type.TEXT                )
            result  = _.encrypt(request)

            encrypted = str(result.encrypted)
            decoded   = base64.b64decode(encrypted)                                             # Should not raise
            assert len(decoded) > len(self.test_text)                                           # Encrypted is larger due to overhead

    def test__encrypt__json(self):                                                              # Test encrypt with JSON type
        with self.routes_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_json_str) ,
                                                  encryption_type = Enum__Encryption_Type.JSON                    )
            result  = _.encrypt(request)

            assert type(result)     is Schema__Encryption__Response
            assert result.success   is True
            assert result.encrypted is not None

    def test__encrypt__json_invalid(self):                                                      # Test encrypt with invalid JSON
        with self.routes_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value("not valid json {]") ,
                                                  encryption_type = Enum__Encryption_Type.JSON                     )
            result  = _.encrypt(request)

            assert result.success   is False
            assert result.error     is not None
            assert result.encrypted is None

    def test__encrypt__data(self):                                                              # Test encrypt with binary data type
        with self.routes_encryption as _:
            data_b64 = base64.b64encode(self.test_binary).decode('utf-8')
            request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(data_b64) ,
                                                   encryption_type = Enum__Encryption_Type.DATA          )
            result   = _.encrypt(request)

            assert type(result)     is Schema__Encryption__Response
            assert result.success   is True
            assert result.encrypted is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # decrypt Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__decrypt__text(self):                                                              # Test decrypt with text type
        with self.routes_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_result   = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.TEXT)
            decrypt_result   = _.decrypt(decrypt_request)

            assert type(decrypt_result)     is Schema__Decryption__Response
            assert decrypt_result.success   is True
            assert decrypt_result.decrypted == self.test_text

    def test__decrypt__json(self):                                                              # Test decrypt with JSON type
        with self.routes_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_json_str) ,
                                                           encryption_type = Enum__Encryption_Type.JSON                    )
            encrypt_result   = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.JSON)
            decrypt_result   = _.decrypt(decrypt_request)

            assert decrypt_result.success   is True
            decrypted_dict = json.loads(str(decrypt_result.decrypted))
            assert decrypted_dict == self.test_json_dict

    def test__decrypt__data(self):                                                              # Test decrypt with binary data type
        with self.routes_encryption as _:
            data_b64 = base64.b64encode(self.test_binary).decode('utf-8')

            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(data_b64) ,
                                                           encryption_type = Enum__Encryption_Type.DATA          )
            encrypt_result   = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.DATA)
            decrypt_result   = _.decrypt(decrypt_request)

            assert decrypt_result.success is True
            decrypted_binary = base64.b64decode(str(decrypt_result.decrypted))
            assert decrypted_binary == self.test_binary

    def test__decrypt__wrong_type(self):                                                        # Test decrypt with wrong type fails
        with self.routes_encryption as _:
            # Encrypt as TEXT
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_result   = _.encrypt(encrypt_request)

            # Try to decrypt as JSON (wrong type)
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.JSON)
            decrypt_result   = _.decrypt(decrypt_request)

            assert decrypt_result.success   is False
            assert decrypt_result.decrypted is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # validate Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__validate__valid_encrypted_data(self):                                             # Test validate with decryptable data
        with self.routes_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_result   = _.encrypt(encrypt_request)

            # Validate
            validate_request  = Schema__Decryption__Validate__Request(encrypted       = encrypt_result.encrypted  ,
                                                                      encryption_type = Enum__Encryption_Type.TEXT)
            validate_result   = _.validate(validate_request)

            assert type(validate_result)       is Schema__Decryption__Validate__Response
            assert validate_result.success     is True
            assert validate_result.can_decrypt is True
            assert validate_result.duration    >  0
            assert validate_result.size_bytes  == len(self.test_text.encode('utf-8'))
            assert validate_result.error       is None
            assert validate_result.timestamp   is not None

    def test__validate__invalid_encrypted_data(self):                                           # Test validate with corrupted data
        with self.routes_encryption as _:
            fake_encrypted = base64.b64encode(b'x' * 100).decode('utf-8')                       # Invalid encrypted data

            validate_request  = Schema__Decryption__Validate__Request(encrypted       = Safe_Str__Encrypted_Value(fake_encrypted) ,
                                                                      encryption_type = Enum__Encryption_Type.TEXT                )
            validate_result   = _.validate(validate_request)

            assert validate_result.success     is False
            assert validate_result.can_decrypt is False
            assert validate_result.error       is not None

    def test__validate__wrong_type(self):                                                       # Test validate with wrong expected type
        with self.routes_encryption as _:
            # Encrypt as TEXT
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_result   = _.encrypt(encrypt_request)

            # Validate as JSON (wrong type)
            validate_request  = Schema__Decryption__Validate__Request(encrypted       = encrypt_result.encrypted  ,
                                                                      encryption_type = Enum__Encryption_Type.JSON)
            validate_result   = _.validate(validate_request)

            assert validate_result.success     is False
            assert validate_result.can_decrypt is False
            assert validate_result.error       is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Round-trip Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__round_trip__unicode(self):                                                        # Test encrypt/decrypt with unicode
        with self.routes_encryption as _:
            unicode_text = "Hello 世界! 🔐🔑 مرحبا"

            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(unicode_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT              )
            encrypt_result   = _.encrypt(encrypt_request)

            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.TEXT)
            decrypt_result   = _.decrypt(decrypt_request)

            assert decrypt_result.success   is True
            assert decrypt_result.decrypted == unicode_text

    def test__round_trip__special_chars(self):                                                  # Test encrypt/decrypt with special chars
        with self.routes_encryption as _:
            special_text = "Special: !@#$%^&*(){}[]|\\:;\"'<>?,./\n\t\r"

            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(special_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT              )
            encrypt_result   = _.encrypt(encrypt_request)

            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_result.encrypted  ,
                                                           encryption_type = Enum__Encryption_Type.TEXT)
            decrypt_result   = _.decrypt(decrypt_request)

            assert decrypt_result.success   is True
            assert decrypt_result.decrypted == special_text

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                               # Test setup_routes configures routes
        routes = Routes__Encryption(service_encryption = self.service_encryption)
        result = routes.setup_routes()

        assert result is None                                                                   # setup_routes doesn't return self in this implementation