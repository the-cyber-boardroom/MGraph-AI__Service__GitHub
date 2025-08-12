from osbot_utils.helpers.Timestamp_Now                                      import Timestamp_Now
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Const__Encryption          import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Safe_Str__NaCl__Public_Key import Safe_Str__NaCl__Public_Key

class Schema__Public_Key__Response(Type_Safe):
    public_key : Safe_Str__NaCl__Public_Key = None
    algorithm  : str                        = NCCL__ALGORITHM
    timestamp  : Timestamp_Now