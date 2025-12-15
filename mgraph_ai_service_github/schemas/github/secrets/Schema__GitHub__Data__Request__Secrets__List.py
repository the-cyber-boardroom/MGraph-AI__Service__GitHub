from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Owner import Safe_Str__GitHub__Repo_Owner
from osbot_utils.type_safe.primitives.domains.git.github.safe_str.Safe_Str__GitHub__Repo_Name  import Safe_Str__GitHub__Repo_Name
from mgraph_ai_service_github.schemas.base.Schema__Request__Data                        import Schema__Request__Data


class Schema__GitHub__Data__Request__Secrets__List(Schema__Request__Data):      # Request data for listing repository secrets
    owner: Safe_Str__GitHub__Repo_Owner                                         # Repository owner (user or organization)
    repo : Safe_Str__GitHub__Repo_Name                                          # Repository name
