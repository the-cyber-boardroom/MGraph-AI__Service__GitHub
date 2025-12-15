from typing import Optional

from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text     import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from mgraph_ai_service_github.schemas.encryption.Const__Encryption               import NCCL__ALGORITHM
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value       import Safe_Str__Encrypted_Value

# todo: fix the bug in OSBot-Utils on Type_Safe Safe_* primitive that is causing the error
#           "Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]" in
#           pydantic_core._pydantic_core.ValidationError: 1 validation error for Schema__Encryption__Response__BaseModel
class Schema__Encryption__Response(Type_Safe):                                          # Schema for encryption response
    algorithm : str                                     = NCCL__ALGORITHM
    encrypted : Optional[Safe_Str__Encrypted_Value]     = None                                     # Base64 encoded encrypted data
    error     : Optional[Safe_Str__Text]                = None                                     # text of any error messages
    success   : bool                                    = False
    timestamp : Timestamp_Now
