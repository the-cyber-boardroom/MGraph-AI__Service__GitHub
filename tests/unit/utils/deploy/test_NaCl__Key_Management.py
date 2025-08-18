import base64
from unittest                                                                                import TestCase
from nacl.public                                                                             import PrivateKey, PublicKey
from osbot_utils.type_safe.primitives.safe_str.cryptography.nacl.Safe_Str__NaCl__Private_Key import Safe_Str__NaCl__Private_Key
from osbot_utils.type_safe.primitives.safe_str.cryptography.nacl.Safe_Str__NaCl__Public_Key  import Safe_Str__NaCl__Public_Key
from osbot_utils.type_safe.primitives.safe_str.cryptography.nacl.Schema__NaCl__Keys          import Schema__NaCl__Keys
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management                        import NaCl__Key_Management


class test_NaCl__Key_Management(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.nacl_key_management = NaCl__Key_Management()
        cls.test_nacl_keys      = cls.nacl_key_management.generate_nacl_keys()

    def test__init__(self):
        with self.nacl_key_management as _:
            assert type(_) is NaCl__Key_Management

    def test_generate_nacl_keys(self):
        with self.nacl_key_management as _:
            nacl_keys   = _.generate_nacl_keys()
            private_key = nacl_keys.private_key
            public_key  = nacl_keys.public_key

            assert type(nacl_keys)   is Schema__NaCl__Keys
            assert type(private_key) is Safe_Str__NaCl__Private_Key
            assert type(public_key)  is Safe_Str__NaCl__Public_Key
            assert len(private_key)  == 64
            assert len(public_key)   == 64
            assert private_key.islower()
            assert public_key.islower()

    def test_generate_nacl_keys__multiple_generations_are_different(self):
        with self.nacl_key_management as _:
            nacl_keys_1 = _.generate_nacl_keys()
            nacl_keys_2 = _.generate_nacl_keys()

            assert nacl_keys_1.private_key != nacl_keys_2.private_key
            assert nacl_keys_1.public_key  != nacl_keys_2.public_key

    def test_private_key_from_hex(self):
        with self.nacl_key_management as _:
            private_key_obj = _.private_key_from_hex(self.test_nacl_keys.private_key)

            assert type(private_key_obj) is PrivateKey

    def test_public_key_from_hex(self):
        with self.nacl_key_management as _:
            public_key_obj = _.public_key_from_hex(self.test_nacl_keys.public_key)

            assert type(public_key_obj) is PublicKey

    def test_encrypt_with_public_key(self):
        with self.nacl_key_management as _:
            test_message = b"Test encryption message"
            encrypted    = _.encrypt_with_public_key(test_message, self.test_nacl_keys.public_key)

            assert type(encrypted) is bytes
            assert len(encrypted)  > len(test_message)                                      # Encrypted is larger
            assert encrypted      != test_message                                           # Should be different

    def test_encrypt_with_public_key_base64(self):
        with self.nacl_key_management as _:
            test_message    = b"Test encryption message"
            encrypted_base64 = _.encrypt_with_public_key_base64(test_message, self.test_nacl_keys.public_key)

            assert type(encrypted_base64) is str
            assert len(encrypted_base64)  > 0

            base64.b64decode(encrypted_base64)                                                      # Should be valid base64

    def test_decrypt_with_private_key(self):
        with self.nacl_key_management as _:
            test_message = b"Test decryption message"
            encrypted    = _.encrypt_with_public_key (test_message, self.test_nacl_keys.public_key )    # Encrypt first
            decrypted    = _.decrypt_with_private_key(encrypted   , self.test_nacl_keys.private_key)    # Then decrypt

            assert decrypted == test_message

    def test_decrypt_with_private_key_base64(self):
        with self.nacl_key_management as _:
            test_message     = b"Test base64 decryption"
            encrypted_base64 = _.encrypt_with_public_key_base64 (test_message    , self.test_nacl_keys.public_key )     # Encrypt and get base64
            decrypted        = _.decrypt_with_private_key_base64(encrypted_base64, self.test_nacl_keys.private_key)     # Decrypt from base64

            assert decrypted == test_message

    def test_validate_key_pair__valid(self):
        with self.nacl_key_management as _:
            assert _.validate_key_pair(self.test_nacl_keys) is True

    def test_validate_key_pair__mismatched(self):
        with self.nacl_key_management as _:
            keys_1 = _.generate_nacl_keys()                                                 # Create two different key pairs
            keys_2 = _.generate_nacl_keys()

            mismatched_keys = Schema__NaCl__Keys(public_key  = keys_1.public_key ,          # Mix them up (public from one, private from another)
                                                 private_key = keys_2.private_key)

            assert _.validate_key_pair(mismatched_keys) is False

    def test_encrypt_string(self):
        with self.nacl_key_management as _:
            test_string      = "Hello, World! 你好世界 🌍"                                       # test_string is "Hello, World! Hello, World 🌍"
            encrypted_base64 = _.encrypt_string(test_string, self.test_nacl_keys.public_key)

            assert type(encrypted_base64) is str
            assert len(encrypted_base64)  > 0
            assert encrypted_base64       != test_string

    def test_decrypt_string(self):
        with self.nacl_key_management as _:
            test_string = "Hello, World! 你好世界 🌍"

            encrypted_base64 = _.encrypt_string(test_string     , self.test_nacl_keys.public_key )              # Encrypt
            decrypted        = _.decrypt_string(encrypted_base64, self.test_nacl_keys.private_key)              # Decrypt

            assert decrypted == test_string

    def test_round_trip__complex_data(self):
        with self.nacl_key_management as _:

            test_cases = [ "Simple ASCII text"                           ,                                      #  Test with various data types
                           "Unicode: 你好世界 مرحبا بالعالم שלום עולם"    ,
                           "Emojis: 🔐🔑🛡️🔒"                           ,
                           "Special chars: !@#$%^&*(){}[]|\\:;\"'<>?,./" ,
                           "Multiline\ntext\nwith\nbreaks"               ,
                           "x" * 1000                                    ]      # Long string

            for test_string in test_cases:
                encrypted = _.encrypt_string(test_string, self.test_nacl_keys.public_key)
                decrypted = _.decrypt_string(encrypted  , self.test_nacl_keys.private_key)
                assert decrypted == test_string , f"Failed for: {test_string[:50]}..."