from typing                                                                               import Optional
from mgraph_ai_service_github.schemas.base.Schema__Response__Data                         import Schema__Response__Data
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Org__Secret__Metadata import Schema__GitHub__Org__Secret__Metadata


class Schema__GitHub__Data__Org__Secret__Get(Schema__Response__Data):           # Response data for getting an org secret
    secret: Optional[Schema__GitHub__Org__Secret__Metadata] = None


class Schema__GitHub__Data__Org__Secret__Create(Schema__Response__Data):        # Response data for creating an org secret
    created: bool = False


class Schema__GitHub__Data__Org__Secret__Update(Schema__Response__Data):        # Response data for updating an org secret
    updated: bool = False


class Schema__GitHub__Data__Org__Secret__Delete(Schema__Response__Data):        # Response data for deleting an org secret
    deleted: bool = False
