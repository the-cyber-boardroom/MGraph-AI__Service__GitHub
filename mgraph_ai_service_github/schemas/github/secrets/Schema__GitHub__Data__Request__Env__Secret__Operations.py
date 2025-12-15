from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Name  import Safe_Str__GitHub__Repo_Name
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text                   import Safe_Str__Text
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                               import Schema__Request__Data
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value                     import Safe_Str__Encrypted_Value
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Name            import Safe_Str__GitHub__Secret_Name


class Schema__GitHub__Data__Request__Env__Secret__Get(Schema__Request__Data):   # Request data for getting an env secret
    owner      : Safe_Str__GitHub__Repo_Owner
    repo       : Safe_Str__GitHub__Repo_Name
    environment: Safe_Str__Text
    secret_name: Safe_Str__GitHub__Secret_Name


class Schema__GitHub__Data__Request__Env__Secret__Create(Schema__Request__Data): # Request data for creating an env secret
    owner          : Safe_Str__GitHub__Repo_Owner
    repo           : Safe_Str__GitHub__Repo_Name
    environment    : Safe_Str__Text
    secret_name    : Safe_Str__GitHub__Secret_Name
    encrypted_value: Safe_Str__Encrypted_Value


class Schema__GitHub__Data__Request__Env__Secret__Delete(Schema__Request__Data): # Request data for deleting an env secret
    owner      : Safe_Str__GitHub__Repo_Owner
    repo       : Safe_Str__GitHub__Repo_Name
    environment: Safe_Str__Text
    secret_name: Safe_Str__GitHub__Secret_Name
