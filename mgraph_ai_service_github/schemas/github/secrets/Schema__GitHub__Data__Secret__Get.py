from typing                                                                          import Optional
from mgraph_ai_service_github.schemas.base.Schema__Response__Data                    import Schema__Response__Data
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Secret__Metadata import Schema__GitHub__Secret__Metadata


class Schema__GitHub__Data__Secret__Get(Schema__Response__Data):                # Response data for getting a single secret
    secret: Optional[Schema__GitHub__Secret__Metadata] = None                   # Secret metadata (no value)
