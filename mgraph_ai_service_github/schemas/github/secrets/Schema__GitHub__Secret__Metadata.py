from typing                                                                  import Optional
from osbot_utils.type_safe.Type_Safe                                         import Type_Safe
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text import Safe_Str__Text
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Name import Safe_Str__GitHub__Secret_Name


class Schema__GitHub__Secret__Metadata(Type_Safe):                              # Metadata for a GitHub secret (value not included)
    name      : Optional[Safe_Str__GitHub__Secret_Name] = None                  # Secret name
    created_at: Optional[Safe_Str__Text]                = None                  # ISO timestamp when created
    updated_at: Optional[Safe_Str__Text]                = None                  # ISO timestamp when last updated
