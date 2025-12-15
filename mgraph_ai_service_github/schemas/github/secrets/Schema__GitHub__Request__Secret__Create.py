from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base                  import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Secret__Create import Schema__GitHub__Data__Request__Secret__Create


class Schema__GitHub__Request__Secret__Create(Schema__GitHub__Request__Base):   # Request schema for creating a repository secret
    request_data: Schema__GitHub__Data__Request__Secret__Create                 # Owner, repo, secret name, and encrypted value
