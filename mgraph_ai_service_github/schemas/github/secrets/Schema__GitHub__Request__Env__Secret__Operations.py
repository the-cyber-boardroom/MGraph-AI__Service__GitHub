from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base                        import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Env__Secrets__List import Schema__GitHub__Data__Request__Env__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Env__Secret__Operations import (
    Schema__GitHub__Data__Request__Env__Secret__Get    ,
    Schema__GitHub__Data__Request__Env__Secret__Create ,
    Schema__GitHub__Data__Request__Env__Secret__Delete )


class Schema__GitHub__Request__Env__Secrets__List(Schema__GitHub__Request__Base): # Request for listing env secrets
    request_data: Schema__GitHub__Data__Request__Env__Secrets__List


class Schema__GitHub__Request__Env__Secret__Get(Schema__GitHub__Request__Base):    # Request for getting an env secret
    request_data: Schema__GitHub__Data__Request__Env__Secret__Get


class Schema__GitHub__Request__Env__Secret__Create(Schema__GitHub__Request__Base): # Request for creating an env secret
    request_data: Schema__GitHub__Data__Request__Env__Secret__Create


class Schema__GitHub__Request__Env__Secret__Update(Schema__GitHub__Request__Base): # Request for updating an env secret
    request_data: Schema__GitHub__Data__Request__Env__Secret__Create               # Same as create


class Schema__GitHub__Request__Env__Secret__Delete(Schema__GitHub__Request__Base): # Request for deleting an env secret
    request_data: Schema__GitHub__Data__Request__Env__Secret__Delete
