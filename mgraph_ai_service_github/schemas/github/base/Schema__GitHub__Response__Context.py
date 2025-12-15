from typing                                                              import Optional
from mgraph_ai_service_github.schemas.base.Schema__Response__Context     import Schema__Response__Context
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Rate_Limit import Schema__GitHub__Rate_Limit


class Schema__GitHub__Response__Context(Schema__Response__Context):             # GitHub response context with rate limit info
    rate_limit: Optional[Schema__GitHub__Rate_Limit] = None                     # GitHub API rate limit information
