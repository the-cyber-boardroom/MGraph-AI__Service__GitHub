from mgraph_ai_service_github.schemas.github.base.Schema__GitHub__Request__Base              import Schema__GitHub__Request__Base
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Secrets__List import Schema__GitHub__Data__Request__Secrets__List


class Schema__GitHub__Request__Secrets__List(Schema__GitHub__Request__Base):    # Request schema for listing repository secrets
    request_data: Schema__GitHub__Data__Request__Secrets__List                  # Owner and repo information
