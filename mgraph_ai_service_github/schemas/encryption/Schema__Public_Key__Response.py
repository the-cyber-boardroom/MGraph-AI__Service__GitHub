from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Public_Key  import Safe_Str__NaCl__Public_Key
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now
from mgraph_ai_service_github.schemas.encryption.Const__Encryption                              import NCCL__ALGORITHM

class Schema__Public_Key__Response(Type_Safe):
    public_key : Safe_Str__NaCl__Public_Key = None
    algorithm  : str                        = NCCL__ALGORITHM
    timestamp  : Timestamp_Now