from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type      import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Decrypted_Value  import Safe_Str__Decrypted_Value


class Schema__Encryption__Request(Type_Safe):               # Schema for encryption request
    value          : Safe_Str__Decrypted_Value  = None
    encryption_type: Enum__Encryption_Type