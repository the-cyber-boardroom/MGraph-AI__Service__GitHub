import base64
import json
import time
from typing                                                                    import Dict
from osbot_utils.decorators.methods.cache_on_self                              import cache_on_self
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.utils.Env                                                     import get_env
from mgraph_ai_service_github.utils.deploy.NaCl__Key_Management                import NaCl__Key_Management
from mgraph_ai_service_github.schemas.encryption.Const__Encryption             import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type         import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Decrypted_Value     import Safe_Str__Decrypted_Value
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value     import Safe_Str__Encrypted_Value
from mgraph_ai_service_github.schemas.encryption.Safe_Str__NaCl__Private_Key   import Safe_Str__NaCl__Private_Key
from mgraph_ai_service_github.schemas.encryption.Safe_Str__NaCl__Public_Key    import Safe_Str__NaCl__Public_Key
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Request   import Schema__Decryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Response  import Schema__Decryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Request  import Schema__Decryption__Validate__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Response import Schema__Decryption__Validate__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Request   import Schema__Encryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Response  import Schema__Encryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Key_Generation__Response import Schema__Key_Generation__Response
from mgraph_ai_service_github.schemas.encryption.Schema__NaCl__Keys            import Schema__NaCl__Keys
from mgraph_ai_service_github.schemas.encryption.Schema__Public_Key__Response  import Schema__Public_Key__Response


class Service__Encryption(Type_Safe):
    nacl_manager    : NaCl__Key_Management
    private_key_hex : str                  = None
    public_key_hex  : str                  = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.nacl_manager:
            self.nacl_manager = NaCl__Key_Management()
        if not self.private_key_hex:
            self.private_key_hex = get_env('SERVICE__AUTH__PRIVATE_KEY', '')
        if not self.public_key_hex:
            self.public_key_hex = get_env('SERVICE__AUTH__PUBLIC_KEY', '')

    @cache_on_self
    def nacl_keys(self) -> Schema__NaCl__Keys:                                  # Get configured NaCl keys
        if not self.private_key_hex or not self.public_key_hex:
            raise ValueError("Encryption keys not configured - SERVICE__AUTH__PRIVATE_KEY and SERVICE__AUTH__PUBLIC_KEY environment variables required")

        return Schema__NaCl__Keys(public_key  = Safe_Str__NaCl__Public_Key (self.public_key_hex ) ,
                                  private_key = Safe_Str__NaCl__Private_Key(self.private_key_hex) )

    def public_key(self) -> Schema__Public_Key__Response:                       # Get public key for encryption
        nacl_keys = self.nacl_keys()
        return Schema__Public_Key__Response(public_key = nacl_keys.public_key)

    def generate_keys(self) -> Schema__Key_Generation__Response:                # Generate new NaCl key pair
        try:
            nacl_keys = self.nacl_manager.generate_nacl_keys()
            return Schema__Key_Generation__Response(success     = True                    ,
                                                   public_key  = nacl_keys.public_key    ,
                                                   private_key = nacl_keys.private_key   )
        except Exception as e:
            return Schema__Key_Generation__Response(success     = False                   ,
                                                   public_key  = None                    ,
                                                   private_key = None                    )

    def encrypt(self, request : Schema__Encryption__Request                         # Encrypt data based on type
                 ) -> Schema__Encryption__Response:                                 # Returns encrypted response
        try:
            nacl_keys = self.nacl_keys()

            if request.encryption_type == Enum__Encryption_Type.TEXT:                                               # Convert value to bytes based on type
                data_bytes = request.value.encode('utf-8')
            elif request.encryption_type == Enum__Encryption_Type.JSON:
                json_obj   = json.loads(request.value)                                                              # Parse and re-stringify to validate JSON
                json_str   = json.dumps(json_obj, separators=(',', ':'))                                            # Compact JSON
                data_bytes = json_str.encode('utf-8')
            elif request.encryption_type == Enum__Encryption_Type.DATA:
                data_bytes = base64.b64decode(request.value)                                                        # Assume value is already base64 encoded binary data
            else:
                raise ValueError(f"Unknown encryption type: {request.encryption_type}")

            encrypted_base64 = self.nacl_manager.encrypt_with_public_key_base64(data_bytes, nacl_keys.public_key)   # Encrypt the data

            return Schema__Encryption__Response(success   = True                                         ,
                                                encrypted = Safe_Str__Encrypted_Value(encrypted_base64)  )

        except json.JSONDecodeError as e:
            return Schema__Encryption__Response(success   = False                                   ,
                                                encrypted = None                                    ,
                                                error     = str(e)                                  )
        except Exception as e:
            return Schema__Encryption__Response(success   = False                                  ,
                                               encrypted = None                                    ,
                                               algorithm = NCCL__ALGORITHM                         )

    def decrypt(self, request : Schema__Decryption__Request                     # Decrypt data based on type
                ) -> Schema__Decryption__Response:                              # Returns decrypted response
        try:
            nacl_keys = self.nacl_keys()

            # Decrypt the data
            decrypted_bytes = self.nacl_manager.decrypt_with_private_key_base64(request.encrypted, nacl_keys.private_key)

            # Convert bytes to appropriate format based on type
            if request.encryption_type == Enum__Encryption_Type.TEXT:
                decrypted_value = decrypted_bytes.decode('utf-8')
            elif request.encryption_type == Enum__Encryption_Type.JSON:
                json_str        = decrypted_bytes.decode('utf-8')
                json_obj        = json.loads(json_str)                          # Validate JSON
                decrypted_value = json.dumps(json_obj, separators=(',', ':'))   # Re-stringify compactly
            elif request.encryption_type == Enum__Encryption_Type.DATA:
                decrypted_value = base64.b64encode(decrypted_bytes).decode('utf-8')
            else:
                raise ValueError(f"Unknown encryption type: {request.encryption_type}")

            return Schema__Decryption__Response(success   = True                                     ,
                                               decrypted = Safe_Str__Decrypted_Value(decrypted_value))

        except json.JSONDecodeError as e:
            return Schema__Decryption__Response(success   = False                                    ,
                                               decrypted = None                                      )
        except Exception as e:
            return Schema__Decryption__Response(success   = False                                    ,
                                               decrypted = None                                      )

    def validate(self, request : Schema__Decryption__Validate__Request          # Validate encrypted data
                  ) -> Schema__Decryption__Validate__Response:                   # Returns validation result
        try:
            nacl_keys  = self.nacl_keys()
            start_time = time.time()

            # Try to decrypt
            decrypted_bytes = self.nacl_manager.decrypt_with_private_key_base64(request.encrypted, nacl_keys.private_key)

            # Validate based on expected type
            if request.encryption_type == Enum__Encryption_Type.TEXT:
                decrypted_value = decrypted_bytes.decode('utf-8')               # Will raise if not valid UTF-8
            elif request.encryption_type == Enum__Encryption_Type.JSON:
                json_str = decrypted_bytes.decode('utf-8')
                json.loads(json_str)                                            # Will raise if not valid JSON
            elif request.encryption_type == Enum__Encryption_Type.DATA:
                pass                                                             # Binary data is always valid

            duration = time.time() - start_time

            return Schema__Decryption__Validate__Response(success     = True                 ,
                                                         can_decrypt = True                  ,
                                                         duration    = duration              ,
                                                         size_bytes  = len(decrypted_bytes)  ,
                                                         error       = None                  )

        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else None

            return Schema__Decryption__Validate__Response(success     = False                ,
                                                         can_decrypt = False                 ,
                                                         duration    = duration              ,
                                                         size_bytes  = None                  ,
                                                         error       = str(e)                )

    def encrypt_text(self, text : str                                           # Convenience method for text encryption
                     ) -> Schema__Encryption__Response:                         # Returns encrypted response
        request = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(text) ,
                                             encryption_type = Enum__Encryption_Type.TEXT      )
        return self.encrypt(request)

    def encrypt_json(self, data : Dict                                          # Convenience method for JSON encryption
                     ) -> Schema__Encryption__Response:                         # Returns encrypted response
        json_str = json.dumps(data, separators=(',', ':'))
        request  = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(json_str) ,
                                              encryption_type = Enum__Encryption_Type.JSON          )
        return self.encrypt(request)

    def encrypt_data(self, data : bytes                                         # Convenience method for binary data encryption
                     ) -> Schema__Encryption__Response:                         # Returns encrypted response
        data_base64 = base64.b64encode(data).decode('utf-8')
        request     = Schema__Encryption__Request(value           = Safe_Str__Decrypted_Value(data_base64) ,
                                                 encryption_type = Enum__Encryption_Type.DATA              )
        return self.encrypt(request)

    def decrypt_text(self, encrypted : str                                      # Convenience method for text decryption
                     ) -> Schema__Decryption__Response:                         # Returns decrypted response
        request = Schema__Decryption__Request(encrypted       = Safe_Str__Encrypted_Value(encrypted) ,
                                             encryption_type = Enum__Encryption_Type.TEXT           )
        return self.decrypt(request)

    def decrypt_json(self, encrypted : str                                      # Convenience method for JSON decryption
                     ) -> Schema__Decryption__Response:                         # Returns decrypted response
        request = Schema__Decryption__Request(encrypted       = Safe_Str__Encrypted_Value(encrypted) ,
                                             encryption_type = Enum__Encryption_Type.JSON           )
        return self.decrypt(request)

    def decrypt_data(self, encrypted : str                                      # Convenience method for binary data decryption
                     ) -> Schema__Decryption__Response:                         # Returns decrypted response
        request = Schema__Decryption__Request(encrypted       = Safe_Str__Encrypted_Value(encrypted) ,
                                             encryption_type = Enum__Encryption_Type.DATA           )
        return self.decrypt(request)