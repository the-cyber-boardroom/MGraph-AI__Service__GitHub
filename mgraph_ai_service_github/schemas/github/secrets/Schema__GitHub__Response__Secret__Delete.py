from typing                                                                             import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response              import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Secret__Delete import Schema__GitHub__Data__Secret__Delete


class Schema__GitHub__Response__Secret__Delete(Schema__GitHub__Response):       # Response schema for deleting a secret
    response_data: Optional[Schema__GitHub__Data__Secret__Delete] = None        # Deletion result or None on failure
