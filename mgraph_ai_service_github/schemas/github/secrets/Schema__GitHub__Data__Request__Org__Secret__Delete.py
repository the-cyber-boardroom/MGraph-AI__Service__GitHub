from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                              import Schema__Request__Data
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Name           import Safe_Str__GitHub__Secret_Name


class Schema__GitHub__Data__Request__Org__Secret__Delete(Schema__Request__Data): # Request data for deleting an org secret
    org        : Safe_Str__GitHub__Repo_Owner                                   # Organization name
    secret_name: Safe_Str__GitHub__Secret_Name                                  # Name of the secret to delete
