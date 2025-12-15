from typing                                                                                    import List, Optional, Literal
from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                               import Schema__Request__Data
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value                     import Safe_Str__Encrypted_Value
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Name            import Safe_Str__GitHub__Secret_Name


class Schema__GitHub__Data__Request__Org__Secret__Create(Schema__Request__Data): # Request data for creating an org secret
    org            : Safe_Str__GitHub__Repo_Owner                               # Organization name
    secret_name    : Safe_Str__GitHub__Secret_Name                              # Name for the new secret
    encrypted_value: Safe_Str__Encrypted_Value                                  # Secret value encrypted with server's public key
    visibility     : Literal['all', 'private', 'selected'] = 'private'          # Who can access this secret
    repo_ids       : Optional[List[int]]                   = None               # Repository IDs if visibility='selected'
