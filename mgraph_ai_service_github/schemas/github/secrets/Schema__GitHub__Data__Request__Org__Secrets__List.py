from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                               import Schema__Request__Data


class Schema__GitHub__Data__Request__Org__Secrets__List(Schema__Request__Data): # Request data for listing organization secrets
    org: Safe_Str__GitHub__Repo_Owner                                           # Organization name
