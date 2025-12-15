from typing                                                                          import List
from mgraph_ai_service_github.schemas.base.Schema__Response__Data                    import Schema__Response__Data
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Secret__Metadata import Schema__GitHub__Secret__Metadata


class Schema__GitHub__Data__Secrets__List(Schema__Response__Data):              # Response data containing list of secrets
    secrets: List[Schema__GitHub__Secret__Metadata]                             # List of secret metadata (no values)
