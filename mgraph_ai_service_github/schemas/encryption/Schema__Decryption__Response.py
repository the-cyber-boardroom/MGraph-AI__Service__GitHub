
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now import Timestamp_Now

from mgraph_ai_service_github.schemas.encryption.Safe_Str__Decrypted_Value  import Safe_Str__Decrypted_Value

class Schema__Decryption__Response(Type_Safe):                                      # Schema for decryption response
    success   : bool                         = False
    decrypted : Safe_Str__Decrypted_Value    = None                                         # Base64 encoded decrypted data
    timestamp : Timestamp_Now