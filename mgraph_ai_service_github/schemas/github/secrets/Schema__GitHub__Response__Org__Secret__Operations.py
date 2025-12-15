from typing                                                                                 import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response                  import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Org__Secret__Operations import (
    Schema__GitHub__Data__Org__Secret__Get    ,
    Schema__GitHub__Data__Org__Secret__Create ,
    Schema__GitHub__Data__Org__Secret__Update ,
    Schema__GitHub__Data__Org__Secret__Delete )


class Schema__GitHub__Response__Org__Secret__Get(Schema__GitHub__Response):     # Response for getting an org secret
    response_data: Optional[Schema__GitHub__Data__Org__Secret__Get] = None


class Schema__GitHub__Response__Org__Secret__Create(Schema__GitHub__Response):  # Response for creating an org secret
    response_data: Optional[Schema__GitHub__Data__Org__Secret__Create] = None


class Schema__GitHub__Response__Org__Secret__Update(Schema__GitHub__Response):  # Response for updating an org secret
    response_data: Optional[Schema__GitHub__Data__Org__Secret__Update] = None


class Schema__GitHub__Response__Org__Secret__Delete(Schema__GitHub__Response):  # Response for deleting an org secret
    response_data: Optional[Schema__GitHub__Data__Org__Secret__Delete] = None
