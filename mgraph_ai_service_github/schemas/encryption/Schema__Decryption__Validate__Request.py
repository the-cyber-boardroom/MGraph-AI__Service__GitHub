from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type      import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value  import Safe_Str__Encrypted_Value

class Schema__Decryption__Validate__Request(Type_Safe):         # Schema for validation request - check if encrypted data can be decrypted
    encrypted      : Safe_Str__Encrypted_Value                  # Encrypted value to validate
    encryption_type: Enum__Encryption_Type                      # Expected type: text, json, or data