from typing                                                                             import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response              import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Secret__Update import Schema__GitHub__Data__Secret__Update


class Schema__GitHub__Response__Secret__Update(Schema__GitHub__Response):       # Response schema for updating a secret
    response_data: Optional[Schema__GitHub__Data__Secret__Update] = None        # Update result or None on failure
