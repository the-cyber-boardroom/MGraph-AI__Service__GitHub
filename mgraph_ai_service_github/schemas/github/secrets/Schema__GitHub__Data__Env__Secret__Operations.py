from typing                                                                          import List, Optional
from mgraph_ai_service_github.schemas.base.Schema__Response__Data                    import Schema__Response__Data
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Secret__Metadata import Schema__GitHub__Secret__Metadata


class Schema__GitHub__Data__Env__Secrets__List(Schema__Response__Data):         # Response data for listing env secrets
    secrets: List[Schema__GitHub__Secret__Metadata]


class Schema__GitHub__Data__Env__Secret__Get(Schema__Response__Data):           # Response data for getting an env secret
    secret: Optional[Schema__GitHub__Secret__Metadata] = None


class Schema__GitHub__Data__Env__Secret__Create(Schema__Response__Data):        # Response data for creating an env secret
    created: bool = False


class Schema__GitHub__Data__Env__Secret__Update(Schema__Response__Data):        # Response data for updating an env secret
    updated: bool = False


class Schema__GitHub__Data__Env__Secret__Delete(Schema__Response__Data):        # Response data for deleting an env secret
    deleted: bool = False
