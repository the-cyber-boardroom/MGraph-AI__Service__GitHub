from typing                                                                             import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response              import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Secret__Create import Schema__GitHub__Data__Secret__Create


class Schema__GitHub__Response__Secret__Create(Schema__GitHub__Response):       # Response schema for creating a secret
    response_data: Optional[Schema__GitHub__Data__Secret__Create] = None        # Creation result or None on failure
