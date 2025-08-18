from osbot_utils.type_safe.Type_Safe                               import Type_Safe
from osbot_utils.type_safe.primitives.safe_int.Timestamp_Now       import Timestamp_Now
from osbot_utils.type_safe.primitives.safe_str.text.Safe_Str__Text import Safe_Str__Text


class Schema__Decryption__Validate__Response(Type_Safe):    # Schema for validation response
    success        : bool                   = False
    can_decrypt    : bool                   = False         # Whether we can decrypt it
    duration       : float                  = None          # How long it takes to decrypt
    size_bytes     : int                    = None          # Size of decrypted data
    error          : Safe_Str__Text         = None          # Error message if validation failed
    timestamp      : Timestamp_Now