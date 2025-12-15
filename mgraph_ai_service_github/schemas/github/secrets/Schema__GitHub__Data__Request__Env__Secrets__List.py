from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Name  import Safe_Str__GitHub__Repo_Name
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                   import Safe_Str__Text
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                               import Schema__Request__Data


class Schema__GitHub__Data__Request__Env__Secrets__List(Schema__Request__Data): # Request data for listing environment secrets
    owner      : Safe_Str__GitHub__Repo_Owner                                   # Repository owner
    repo       : Safe_Str__GitHub__Repo_Name                                    # Repository name
    environment: Safe_Str__Text                   = None                        # Environment name  # todo: see what better Schema we shouldbe using here
