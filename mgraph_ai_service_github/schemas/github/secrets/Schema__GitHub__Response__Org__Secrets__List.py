from typing                                                                                  import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response                   import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Org__Secrets__List import Schema__GitHub__Data__Org__Secrets__List


class Schema__GitHub__Response__Org__Secrets__List(Schema__GitHub__Response):   # Response schema for listing organization secrets
    response_data: Optional[Schema__GitHub__Data__Org__Secrets__List] = None    # List of org secrets or None on failure
