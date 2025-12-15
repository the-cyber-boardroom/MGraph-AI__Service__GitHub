from typing                                                                      import Optional
from osbot_utils.type_safe.Type_Safe                                             import Type_Safe
from mgraph_ai_service_github.schemas.base.Schema__Response__Data                import Schema__Response__Data
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response__Context import Schema__GitHub__Response__Context


class Schema__GitHub__Response(Type_Safe):                                      # Base response schema for all GitHub operations
    response_context: Schema__GitHub__Response__Context                         # Execution metadata with rate limit info
    response_data   : Optional[Schema__Response__Data] = None                   # Operation-specific response data
