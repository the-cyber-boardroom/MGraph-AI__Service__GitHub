from typing                                                                          import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response           import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Secret__Get import Schema__GitHub__Data__Secret__Get


class Schema__GitHub__Response__Secret__Get(Schema__GitHub__Response):          # Response schema for getting a single secret
    response_data: Optional[Schema__GitHub__Data__Secret__Get] = None           # Secret metadata or None on failure
