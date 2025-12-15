from typing                                                                      import List, Optional
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from mgraph_ai_service_github.schemas.base.Enum__HTTP__Status                    import Enum__HTTP__Status
from mgraph_ai_service_github.schemas.base.Enum__Error__Type                     import Enum__Error__Type
from mgraph_ai_service_github.schemas.safe_str.Safe_Str__Error_Message           import Safe_Str__Text_Message


class Schema__Response__Context(Type_Safe):                                     # Response context containing execution metadata
    success    : bool                       = False                             # Overall operation success
    status_code: Enum__HTTP__Status         = Enum__HTTP__Status.SERVER_ERROR_500
    duration   : Optional[float]            = None                              # Execution duration in seconds
    timestamp  : Timestamp_Now                                                  # Auto-populated response timestamp
    messages   : List[Safe_Str__Text_Message]                                   # Informational messages
    errors     : List[Safe_Str__Text_Message]                                   # Error details
    error_type : Enum__Error__Type          = Enum__Error__Type.NONE            # Error classification
