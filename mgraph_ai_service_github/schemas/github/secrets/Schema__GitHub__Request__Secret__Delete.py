from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base                  import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Secret__Delete import Schema__GitHub__Data__Request__Secret__Delete


class Schema__GitHub__Request__Secret__Delete(Schema__GitHub__Request__Base):   # Request schema for deleting a repository secret
    request_data: Schema__GitHub__Data__Request__Secret__Delete                 # Owner, repo, and secret name
