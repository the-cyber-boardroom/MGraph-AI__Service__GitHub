from typing                                                                 import Optional
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.base.Schema__Request__Data            import Schema__Request__Data
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value  import Safe_Str__Encrypted_Value


class Schema__GitHub__Request__Base(Type_Safe):                                 # Base request schema for all GitHub operations
    encrypted_pat: Safe_Str__Encrypted_Value                                    # NaCl-encrypted GitHub PAT (base64 encoded)
    request_data : Optional[Schema__Request__Data] = None                       # Operation-specific request data
