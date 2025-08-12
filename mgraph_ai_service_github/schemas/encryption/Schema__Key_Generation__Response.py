from osbot_utils.helpers.Timestamp_Now                                          import Timestamp_Now
from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Safe_Str__NaCl__Private_Key    import Safe_Str__NaCl__Private_Key
from mgraph_ai_service_github.schemas.encryption.Safe_Str__NaCl__Public_Key     import Safe_Str__NaCl__Public_Key


class Schema__Key_Generation__Response(Type_Safe):                          # Schema for key generation response
    success     : bool                          = False
    public_key  : Safe_Str__NaCl__Public_Key    = None                      # Public key (hex)
    private_key : Safe_Str__NaCl__Private_Key   = None                      # Private key (hex) - only in generation
    timestamp   : Timestamp_Now