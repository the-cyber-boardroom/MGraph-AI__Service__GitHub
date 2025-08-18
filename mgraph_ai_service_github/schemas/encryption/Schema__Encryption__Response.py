from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now                import Timestamp_Now
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text          import Safe_Str__Text
from mgraph_ai_service_github.schemas.encryption.Const__Encryption          import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value  import Safe_Str__Encrypted_Value



class Schema__Encryption__Response(Type_Safe):                                          # Schema for encryption response
    algorithm : str = NCCL__ALGORITHM
    encrypted : Safe_Str__Encrypted_Value    = None                                     # Base64 encoded encrypted data
    error     : Safe_Str__Text               = None                                     # text of any error messages
    success   : bool = False
    timestamp : Timestamp_Now
