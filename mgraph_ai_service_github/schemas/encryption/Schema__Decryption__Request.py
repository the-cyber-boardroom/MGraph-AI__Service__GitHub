from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type      import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value  import Safe_Str__Encrypted_Value


class Schema__Decryption__Request(Type_Safe):           # Schema for decryption request
    encrypted : Safe_Str__Encrypted_Value               # Base64 encoded encrypted data to decrypt
    encryption_type: Enum__Encryption_Type