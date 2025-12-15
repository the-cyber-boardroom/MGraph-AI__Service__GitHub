from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base              import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Secret__Get import Schema__GitHub__Data__Request__Secret__Get


class Schema__GitHub__Request__Secret__Get(Schema__GitHub__Request__Base):      # Request schema for getting a single secret
    request_data: Schema__GitHub__Data__Request__Secret__Get                    # Owner, repo, and secret name
