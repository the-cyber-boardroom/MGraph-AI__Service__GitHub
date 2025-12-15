from typing                                                                                  import Optional
from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Response                   import Schema__GitHub__Response
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Env__Secret__Operations import (
    Schema__GitHub__Data__Env__Secrets__List  ,
    Schema__GitHub__Data__Env__Secret__Get    ,
    Schema__GitHub__Data__Env__Secret__Create ,
    Schema__GitHub__Data__Env__Secret__Update ,
    Schema__GitHub__Data__Env__Secret__Delete )


class Schema__GitHub__Response__Env__Secrets__List(Schema__GitHub__Response):   # Response for listing env secrets
    response_data: Optional[Schema__GitHub__Data__Env__Secrets__List] = None


class Schema__GitHub__Response__Env__Secret__Get(Schema__GitHub__Response):     # Response for getting an env secret
    response_data: Optional[Schema__GitHub__Data__Env__Secret__Get] = None


class Schema__GitHub__Response__Env__Secret__Create(Schema__GitHub__Response):  # Response for creating an env secret
    response_data: Optional[Schema__GitHub__Data__Env__Secret__Create] = None


class Schema__GitHub__Response__Env__Secret__Update(Schema__GitHub__Response):  # Response for updating an env secret
    response_data: Optional[Schema__GitHub__Data__Env__Secret__Update] = None


class Schema__GitHub__Response__Env__Secret__Delete(Schema__GitHub__Response):  # Response for deleting an env secret
    response_data: Optional[Schema__GitHub__Data__Env__Secret__Delete] = None
