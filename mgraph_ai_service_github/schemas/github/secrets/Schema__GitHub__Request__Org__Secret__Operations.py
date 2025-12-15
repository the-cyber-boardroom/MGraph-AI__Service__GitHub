from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base                      import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Get    import Schema__GitHub__Data__Request__Org__Secret__Get
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Create import Schema__GitHub__Data__Request__Org__Secret__Create
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Delete import Schema__GitHub__Data__Request__Org__Secret__Delete


class Schema__GitHub__Request__Org__Secret__Get(Schema__GitHub__Request__Base):    # Request for getting an org secret
    request_data: Schema__GitHub__Data__Request__Org__Secret__Get


class Schema__GitHub__Request__Org__Secret__Create(Schema__GitHub__Request__Base): # Request for creating an org secret
    request_data: Schema__GitHub__Data__Request__Org__Secret__Create


class Schema__GitHub__Request__Org__Secret__Update(Schema__GitHub__Request__Base): # Request for updating an org secret (same as create)
    request_data: Schema__GitHub__Data__Request__Org__Secret__Create


class Schema__GitHub__Request__Org__Secret__Delete(Schema__GitHub__Request__Base): # Request for deleting an org secret
    request_data: Schema__GitHub__Data__Request__Org__Secret__Delete
