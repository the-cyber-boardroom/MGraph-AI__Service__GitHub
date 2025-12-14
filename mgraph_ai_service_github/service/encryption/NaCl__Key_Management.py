import base64
from nacl.public                                                                                import PrivateKey, PublicKey, SealedBox
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Private_Key import Safe_Str__NaCl__Private_Key
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Public_Key  import Safe_Str__NaCl__Public_Key
from osbot_utils.type_safe.primitives.domains.cryptography.schemas.Schema__NaCl__Keys           import Schema__NaCl__Keys


class NaCl__Key_Management(Type_Safe):

    def generate_nacl_keys(self) -> Schema__NaCl__Keys:                         # Generate a new NaCl key pair for SealedBox encryption/decryption
        nacl__private_key = PrivateKey.generate()
        nacl__public_key  = nacl__private_key.public_key
        
        private_key = Safe_Str__NaCl__Private_Key(bytes(nacl__private_key).hex())
        public_key  = Safe_Str__NaCl__Public_Key (bytes(nacl__public_key ).hex())
        
        nacl_keys = Schema__NaCl__Keys(public_key  = public_key  ,
                                       private_key = private_key )
        return nacl_keys
    
    def private_key_from_hex(self, private_key_hex : Safe_Str__NaCl__Private_Key        # Convert hex string to PrivateKey object
                              ) -> PrivateKey:                                          # Returns nacl.public.PrivateKey
        return PrivateKey(bytes.fromhex(private_key_hex))
    
    def public_key_from_hex(self, public_key_hex : Safe_Str__NaCl__Public_Key           # Convert hex string to PublicKey object
                             ) -> PublicKey:                                            # Returns nacl.public.PublicKey
        return PublicKey(bytes.fromhex(public_key_hex))
    
    def encrypt_with_public_key(self, message        : bytes                      ,     # Encrypt message with public key
                                      public_key_hex : Safe_Str__NaCl__Public_Key       # Public key in hex format
                                 ) -> bytes:                                            # Returns encrypted bytes
        public_key = self.public_key_from_hex(public_key_hex)
        sealed_box = SealedBox(public_key)
        return sealed_box.encrypt(message)
    
    def encrypt_with_public_key_base64(self, message        : bytes                      ,  # Encrypt and base64 encode
                                             public_key_hex : Safe_Str__NaCl__Public_Key    # Public key in hex format
                                        ) -> str:                                           # Returns base64 encoded encrypted data
        encrypted = self.encrypt_with_public_key(message, public_key_hex)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_with_private_key(self, encrypted_data  : bytes                       ,      # Decrypt with private key
                                       private_key_hex : Safe_Str__NaCl__Private_Key        # Private key in hex format
                                  ) -> bytes:                                               # Returns decrypted bytes
        private_key = self.private_key_from_hex(private_key_hex)
        sealed_box  = SealedBox(private_key)
        return sealed_box.decrypt(encrypted_data)
    
    def decrypt_with_private_key_base64(self, encrypted_base64 : str                        ,   # Decrypt base64 encoded data
                                              private_key_hex  : Safe_Str__NaCl__Private_Key    # Private key in hex format
                                         ) -> bytes:                                            # Returns decrypted bytes
        encrypted_data = base64.b64decode(encrypted_base64)
        return self.decrypt_with_private_key(encrypted_data, private_key_hex)
    
    def validate_key_pair(self, nacl_keys : Schema__NaCl__Keys                                  # Validate that a key pair works correctly
                           ) -> bool:                                                           # Returns True if keys are valid pair
        try:
            test_message = b"Validation test message"
            encrypted    = self.encrypt_with_public_key(test_message, nacl_keys.public_key)        # Encrypt with public key
            decrypted    = self.decrypt_with_private_key(encrypted, nacl_keys.private_key)         # Decrypt with private key
            return decrypted == test_message                                                       # Check if round-trip worked
        except Exception:
            return False
    
    def encrypt_string(self, text           : str                        ,                  # Encrypt a string (convenience method)
                             public_key_hex : Safe_Str__NaCl__Public_Key                    # Public key in hex format
                        ) -> str:                                                           # Returns base64 encoded encrypted string
        return self.encrypt_with_public_key_base64(text.encode('utf-8'), public_key_hex)
    
    def decrypt_string(self, encrypted_base64 : str                            ,            # Decrypt a string (convenience method)
                            private_key_hex   : Safe_Str__NaCl__Private_Key                 # Private key in hex format
                      ) -> str:                                                             # Returns decrypted string
        decrypted_bytes = self.decrypt_with_private_key_base64(encrypted_base64, private_key_hex)
        return decrypted_bytes.decode('utf-8')