import pytest
import base64
import json
from unittest                                                                                   import TestCase
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Private_Key import Safe_Str__NaCl__Private_Key
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Public_Key  import Safe_Str__NaCl__Public_Key
from osbot_utils.type_safe.primitives.domains.cryptography.schemas.Schema__NaCl__Keys           import Schema__NaCl__Keys
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management                           import NaCl__Key_Management
from mgraph_ai_service_github.service.encryption.Service__Encryption                            import Service__Encryption
from mgraph_ai_service_github.schemas.encryption.Const__Encryption                              import NCCL__ALGORITHM, ERROR_MESSAGE__ENCRYPTION_KEYS_NOT_CONFIGURED
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


class test_Service__Encryption(TestCase):

    @classmethod
    def setUpClass(cls):
        nacl_manager             = NaCl__Key_Management()
        test_keys                = nacl_manager.generate_nacl_keys()
        cls.test_public_key_hex  = test_keys.public_key
        cls.test_private_key_hex = test_keys.private_key

        cls.service_encryption = Service__Encryption(private_key_hex = cls.test_private_key_hex ,
                                                     public_key_hex  = cls.test_public_key_hex  )

        cls.test_text      = "Hello, World! This is a test message. 你好世界 🌍"
        cls.test_json_dict = { "name"     : "Test User"          ,
                               "id"       : 12345                ,
                               "active"   : True                 ,
                               "tags"     : ["test", "encryption"]}
        cls.test_json_str  = json.dumps(cls.test_json_dict, separators=(',', ':'))
        cls.test_binary    = b"Binary test data \x00\x01\x02\x03\xff"
        cls.test_data_b64  = base64.b64encode(cls.test_binary).decode('utf-8')

    def test__setUpClass(self):
        with self.service_encryption as _:
            assert type(_)                 is Service__Encryption
            assert type(_.nacl_manager)    is NaCl__Key_Management
            assert _.private_key_hex       == self.test_private_key_hex
            assert _.public_key_hex        == self.test_public_key_hex

    def test_nacl_keys(self):
        with self.service_encryption as _:
            nacl_keys = _.nacl_keys()

            assert type(nacl_keys)             is Schema__NaCl__Keys
            assert type(nacl_keys.public_key)  is Safe_Str__NaCl__Public_Key
            assert type(nacl_keys.private_key) is Safe_Str__NaCl__Private_Key
            assert nacl_keys.public_key        == self.test_public_key_hex
            assert nacl_keys.private_key       == self.test_private_key_hex

    def test_nacl_keys__missing(self):
        service = Service__Encryption(private_key_hex = "" ,
                                      public_key_hex  = "" )

        with pytest.raises(ValueError, match=ERROR_MESSAGE__ENCRYPTION_KEYS_NOT_CONFIGURED):
            service.nacl_keys()


    def test_public_key(self):
        with self.service_encryption as _:
            response = _.public_key()

            assert type(response)            is Schema__Public_Key__Response
            assert type(response.public_key) is Safe_Str__NaCl__Public_Key
            assert response.public_key       == self.test_public_key_hex
            assert response.algorithm        == NCCL__ALGORITHM
            assert response.timestamp        is not None

    def test_public_key__no_keys_configured(self):
        with pytest.raises(ValueError, match=ERROR_MESSAGE__ENCRYPTION_KEYS_NOT_CONFIGURED):
            Service__Encryption().public_key()

    def test_generate_keys(self):
        with self.service_encryption as _:
            response = _.generate_keys()

            assert type(response)               is Schema__Key_Generation__Response
            assert response.success             is True
            assert type(response.public_key)   is Safe_Str__NaCl__Public_Key
            assert type(response.private_key)  is Safe_Str__NaCl__Private_Key
            assert len(response.public_key)    == 64
            assert len(response.private_key)   == 64
            assert response.public_key         != response.private_key
            assert response.timestamp          is not None

    def test_generate_keys__multiple_calls_different(self):
        with self.service_encryption as _:
            response1 = _.generate_keys()
            response2 = _.generate_keys()

            assert response1.public_key  != response2.public_key
            assert response1.private_key != response2.private_key

    def test_encrypt__text(self):
        with self.service_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                  encryption_type = Enum__Encryption_Type.TEXT                )
            response = _.encrypt(request)

            assert type(response)           is Schema__Encryption__Response
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value
            assert response.algorithm       == NCCL__ALGORITHM
            assert response.timestamp       is not None
            assert len(response.encrypted)  > len(self.test_text)

            assert base64.b64decode(response.encrypted)                 # Verify it's valid base64

    def test_encrypt__json(self):
        with self.service_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_json_str) ,
                                                  encryption_type = Enum__Encryption_Type.JSON                    )
            response = _.encrypt(request)

            assert type(response)           is Schema__Encryption__Response
            assert response.error           is None
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value
            assert len(response.encrypted)  > len(self.test_json_str)

    def test_encrypt__json_invalid(self):
        with self.service_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value("not valid json {]") ,
                                                 encryption_type = Enum__Encryption_Type.JSON                      )
            response = _.encrypt(request)

            assert response.success   is False
            assert response.error     == 'Expecting value: line 1 column 1 (char 0)'
            assert response.encrypted is None

    def test_encrypt__data(self):
        with self.service_encryption as _:
            request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_data_b64) ,
                                                 encryption_type = Enum__Encryption_Type.DATA                     )
            response = _.encrypt(request)

            assert type(response)           is Schema__Encryption__Response
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value
            assert len(response.encrypted)  > len(self.test_data_b64)

    def test_decrypt__text(self):
        with self.service_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                          encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_response = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_response.encrypted ,
                                                          encryption_type = Enum__Encryption_Type.TEXT )
            decrypt_response = _.decrypt(decrypt_request)

            assert type(decrypt_response)           is Schema__Decryption__Response
            assert decrypt_response.success         is True
            assert type(decrypt_response.decrypted) is Safe_Str__Decrypted_Value
            assert decrypt_response.decrypted       == self.test_text
            assert decrypt_response.timestamp       is not None

    def test_decrypt__json(self):
        with self.service_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_json_str) ,
                                                          encryption_type = Enum__Encryption_Type.JSON                    )
            encrypt_response = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_response.encrypted ,
                                                          encryption_type = Enum__Encryption_Type.JSON )
            decrypt_response = _.decrypt(decrypt_request)

            assert decrypt_response.success   is True
            assert decrypt_response.decrypted is not None

            # Verify JSON is valid and matches original
            decrypted_dict = json.loads(decrypt_response.decrypted)
            assert decrypted_dict == self.test_json_dict

    def test_decrypt__data(self):
        with self.service_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_data_b64) ,
                                                          encryption_type = Enum__Encryption_Type.DATA                     )
            encrypt_response = _.encrypt(encrypt_request)

            # Then decrypt
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_response.encrypted ,
                                                          encryption_type = Enum__Encryption_Type.DATA )
            decrypt_response = _.decrypt(decrypt_request)

            assert decrypt_response.success   is True
            assert decrypt_response.decrypted == self.test_data_b64

            # Verify binary data matches
            decrypted_binary = base64.b64decode(decrypt_response.decrypted)
            assert decrypted_binary == self.test_binary

    def test_decrypt__wrong_type(self):
        with self.service_encryption as _:
            # Encrypt as TEXT
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                          encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_response = _.encrypt(encrypt_request)

            # Try to decrypt as JSON (wrong type)
            decrypt_request  = Schema__Decryption__Request(encrypted       = encrypt_response.encrypted ,
                                                          encryption_type = Enum__Encryption_Type.JSON )
            decrypt_response = _.decrypt(decrypt_request)

            assert decrypt_response.success   is False
            assert decrypt_response.decrypted is None

    def test_decrypt__invalid_encrypted_data(self):
        with self.service_encryption as _:
            invalid_encrypted = base64.b64encode(b"not encrypted data" * 10).decode('utf-8')

            decrypt_request  = Schema__Decryption__Request(encrypted       = Safe_Str__Encrypted_Value(invalid_encrypted) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                    )
            decrypt_response = _.decrypt(decrypt_request)

            assert decrypt_response.success   is False
            assert decrypt_response.decrypted is None

    def test_validate__valid(self):
        with self.service_encryption as _:
            # First encrypt
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_response = _.encrypt(encrypt_request)

            # Validate
            validate_request  = Schema__Decryption__Validate__Request(encrypted       = encrypt_response.encrypted ,
                                                                      encryption_type = Enum__Encryption_Type.TEXT )
            validate_response = _.validate(validate_request)

            assert type(validate_response)       is Schema__Decryption__Validate__Response
            assert validate_response.success     is True
            assert validate_response.can_decrypt is True
            assert validate_response.duration    >  0
            assert validate_response.size_bytes  == len(self.test_text.encode('utf-8'))
            assert validate_response.error       is None
            assert validate_response.timestamp   is not None

    def test_validate__invalid(self):
        with self.service_encryption as _:
            invalid_encrypted = base64.b64encode(b"not encrypted data" * 10).decode('utf-8')

            validate_request  = Schema__Decryption__Validate__Request(encrypted       = Safe_Str__Encrypted_Value(invalid_encrypted) ,
                                                                     encryption_type = Enum__Encryption_Type.TEXT                    )
            validate_response = _.validate(validate_request)

            assert validate_response.success     is False
            assert validate_response.can_decrypt is False
            assert validate_response.size_bytes  is None
            assert validate_response.error       is not None

    def test_validate__wrong_type(self):
        with self.service_encryption as _:
            # Encrypt as TEXT
            encrypt_request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(self.test_text) ,
                                                           encryption_type = Enum__Encryption_Type.TEXT                )
            encrypt_response = _.encrypt(encrypt_request)

            # Validate as JSON (wrong type)
            validate_request  = Schema__Decryption__Validate__Request(encrypted       = encrypt_response.encrypted ,
                                                                      encryption_type = Enum__Encryption_Type.JSON )
            validate_response = _.validate(validate_request)

            assert validate_response.success     is False
            assert validate_response.can_decrypt is False
            assert validate_response.error       is not None

    def test_encrypt_text(self):
        with self.service_encryption as _:
            response = _.encrypt_text(self.test_text)

            assert type(response)           is Schema__Encryption__Response
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value

    def test_encrypt_json(self):
        with self.service_encryption as _:
            response = _.encrypt_json(self.test_json_dict)

            assert type(response)           is Schema__Encryption__Response
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value

    def test_encrypt_data(self):
        with self.service_encryption as _:
            response = _.encrypt_data(self.test_binary)

            assert type(response)           is Schema__Encryption__Response
            assert response.success         is True
            assert type(response.encrypted) is Safe_Str__Encrypted_Value

    def test_decrypt_text(self):
        with self.service_encryption as _:
            encrypt_response = _.encrypt_text(self.test_text)                           # Encrypt first
            decrypt_response = _.decrypt_text(encrypt_response.encrypted)               # Decrypt

            assert type(decrypt_response)     is Schema__Decryption__Response
            assert decrypt_response.success   is True
            assert decrypt_response.decrypted == self.test_text

    def test_decrypt_json(self):
        with self.service_encryption as _:
            encrypt_response = _.encrypt_json(self.test_json_dict)              # Encrypt first
            decrypt_response = _.decrypt_json(encrypt_response.encrypted)       # Decrypt

            assert decrypt_response.success is True
            decrypted_dict = json.loads(decrypt_response.decrypted)
            assert decrypted_dict == self.test_json_dict

    def test_decrypt_data(self):
        with self.service_encryption as _:
            encrypt_response = _.encrypt_data(self.test_binary)                 # Encrypt first
            decrypt_response = _.decrypt_data(encrypt_response.encrypted)       # Decrypt

            assert decrypt_response.success is True
            decrypted_binary = base64.b64decode(decrypt_response.decrypted)
            assert decrypted_binary == self.test_binary

    def test_round_trip__all_types(self):
        with self.service_encryption as _:
            # Test TEXT round trip
            text_encrypted = _.encrypt_text(self.test_text)
            text_decrypted = _.decrypt_text(text_encrypted.encrypted)
            assert text_decrypted.decrypted == self.test_text

            # Test JSON round trip
            json_encrypted = _.encrypt_json(self.test_json_dict)
            json_decrypted = _.decrypt_json(json_encrypted.encrypted)
            assert json.loads(json_decrypted.decrypted) == self.test_json_dict

            # Test DATA round trip
            data_encrypted = _.encrypt_data(self.test_binary)
            data_decrypted = _.decrypt_data(data_encrypted.encrypted)
            assert base64.b64decode(data_decrypted.decrypted) == self.test_binary

    def test_round_trip__unicode_and_special_chars(self):
        with self.service_encryption as _:
            test_cases = [ "Simple ASCII"                                          ,
                          "Unicode: 你好世界 مرحبا שלום"                          ,
                          "Emojis: 🔐🔑🛡️🔒"                                      ,
                          "Special: !@#$%^&*(){}[]|\\:;\"'<>?,./\n\t\r"          ,
                          "Mixed: Hello世界🌍\n\tSpecial!@#"                      ]

            for test_string in test_cases:
                encrypted = _.encrypt_text(test_string)
                decrypted = _.decrypt_text(encrypted.encrypted)
                assert decrypted.decrypted == test_string

    def test_performance__validate_timing(self):
        with self.service_encryption as _:
            # Create encrypted data
            encrypt_response = _.encrypt_text("Performance test")

            # Validate multiple times to check timing
            durations = []
            for i in range(5):
                validate_request  = Schema__Decryption__Validate__Request(encrypted       = encrypt_response.encrypted ,
                                                                         encryption_type = Enum__Encryption_Type.TEXT )
                validate_response = _.validate(validate_request)
                durations.append(validate_response.duration)

            # All durations should be reasonable (< 1 second)
            for duration in durations:
                assert duration > 0
                assert duration < 1.0