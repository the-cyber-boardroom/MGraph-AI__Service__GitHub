import base64
from typing                                                                           import Dict, Tuple, Optional
from nacl.public                                                                      import PrivateKey, PublicKey, SealedBox
from osbot_utils.type_safe.Type_Safe                                                  import Type_Safe
from mgraph_ai_service_github.surrogates.github.schemas.Schema__Surrogate__Public_Key import Schema__Surrogate__Public_Key


class GitHub__API__Surrogate__Keys(Type_Safe):                                  # Manages NaCl key pairs for secret encryption
    
    _key_pairs : Dict[str, Tuple[PrivateKey, PublicKey]]                        # scope_id -> (private, public)
    _key_ids   : Dict[str, str]                                                 # scope_id -> key_id
    _id_counter: int                                                            # Counter for generating key IDs
    
    def setup(self) -> 'GitHub__API__Surrogate__Keys':                          # Initialize key storage
        self._key_pairs  = {}
        self._key_ids    = {}
        self._id_counter = 568250167242549743                                   # Start with realistic key ID
        return self
    
    def reset(self) -> 'GitHub__API__Surrogate__Keys':                          # Clear all keys
        return self.setup()
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Scope ID generation
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def scope_id_for_repo(self, owner: str, repo: str) -> str:                  # Generate scope ID for repository secrets
        return f"repo:{owner}/{repo}"
    
    def scope_id_for_env(self, owner: str, repo: str, environment: str) -> str: # Generate scope ID for environment secrets
        return f"env:{owner}/{repo}/{environment}"
    
    def scope_id_for_org(self, org: str) -> str:                                # Generate scope ID for organization secrets
        return f"org:{org}"
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Key pair management
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def _generate_key_id(self) -> str:                                          # Generate unique key ID
        key_id            = str(self._id_counter)
        self._id_counter += 1
        return key_id
    
    def get_or_create_key_pair(self, scope_id: str                              # Get or create key pair for scope
                               ) -> Schema__Surrogate__Public_Key:
        if scope_id not in self._key_pairs:
            private_key = PrivateKey.generate()
            public_key  = private_key.public_key
            key_id      = self._generate_key_id()
            
            self._key_pairs[scope_id] = (private_key, public_key)
            self._key_ids[scope_id]   = key_id
        
        _, public_key = self._key_pairs[scope_id]
        key_id        = self._key_ids[scope_id]
        
        # Encode public key as base64 (GitHub's format)
        public_key_b64 = base64.b64encode(bytes(public_key)).decode('utf-8')
        
        return Schema__Surrogate__Public_Key(key_id = key_id         ,
                                             key    = public_key_b64 )
    
    def get_public_key(self, scope_id: str) -> Optional[Schema__Surrogate__Public_Key]:
        if scope_id not in self._key_pairs:
            return None
        return self.get_or_create_key_pair(scope_id)
    
    def get_key_id(self, scope_id: str) -> Optional[str]:                       # Get key ID for scope
        return self._key_ids.get(scope_id)
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Encryption/Decryption
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def encrypt_secret(self, scope_id: str, plaintext: str) -> str:             # Encrypt a secret value
        if scope_id not in self._key_pairs:
            self.get_or_create_key_pair(scope_id)                               # Create key pair if needed
        
        _, public_key = self._key_pairs[scope_id]
        sealed_box    = SealedBox(public_key)
        encrypted     = sealed_box.encrypt(plaintext.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_secret(self, scope_id: str, encrypted_value: str) -> str:       # Decrypt a secret value (for validation/debugging)
        if scope_id not in self._key_pairs:
            raise ValueError(f"No key pair found for scope: {scope_id}")
        
        private_key, _ = self._key_pairs[scope_id]
        sealed_box     = SealedBox(private_key)
        encrypted_data = base64.b64decode(encrypted_value)
        decrypted      = sealed_box.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def validate_encrypted_value(self, scope_id: str, encrypted_value: str      # Validate that encrypted value can be decrypted
                                  ) -> bool:
        try:
            self.decrypt_secret(scope_id, encrypted_value)
            return True
        except Exception:
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # Convenience methods for common scope patterns
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_repo_public_key(self, owner: str, repo: str                         # Get public key for repository
                            ) -> Schema__Surrogate__Public_Key:
        scope_id = self.scope_id_for_repo(owner, repo)
        return self.get_or_create_key_pair(scope_id)
    
    def get_env_public_key(self, owner: str, repo: str, environment: str        # Get public key for environment
                           ) -> Schema__Surrogate__Public_Key:
        scope_id = self.scope_id_for_env(owner, repo, environment)
        return self.get_or_create_key_pair(scope_id)
    
    def get_org_public_key(self, org: str                                       # Get public key for organization
                           ) -> Schema__Surrogate__Public_Key:
        scope_id = self.scope_id_for_org(org)
        return self.get_or_create_key_pair(scope_id)
