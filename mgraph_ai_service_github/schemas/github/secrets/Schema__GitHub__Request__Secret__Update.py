from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base                  import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Secret__Update import Schema__GitHub__Data__Request__Secret__Update


class Schema__GitHub__Request__Secret__Update(Schema__GitHub__Request__Base):   # Request schema for updating a repository secret
    request_data: Schema__GitHub__Data__Request__Secret__Update                 # Owner, repo, secret name, and new encrypted value
