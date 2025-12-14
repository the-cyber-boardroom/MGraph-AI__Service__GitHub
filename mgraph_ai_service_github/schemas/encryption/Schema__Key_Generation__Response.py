
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Private_Key import Safe_Str__NaCl__Private_Key
from osbot_utils.type_safe.primitives.domains.cryptography.safe_str.Safe_Str__NaCl__Public_Key  import Safe_Str__NaCl__Public_Key
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now                import Timestamp_Now


class Schema__Key_Generation__Response(Type_Safe):                          # Schema for key generation response
    success     : bool                          = False
    public_key  : Safe_Str__NaCl__Public_Key    = None                      # Public key (hex)
    private_key : Safe_Str__NaCl__Private_Key   = None                      # Private key (hex) - only in generation
    timestamp   : Timestamp_Now