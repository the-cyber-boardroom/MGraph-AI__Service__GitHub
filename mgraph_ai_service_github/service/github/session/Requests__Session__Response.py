from typing                                  import Dict, Any
from osbot_utils.type_safe.Type_Safe         import Type_Safe

class Requests__Session__Response(Type_Safe):                                   # Abstract response interface
    status_code : int = 0

    def json(self) -> Dict[str, Any]:                                           # Parse JSON response
        raise NotImplementedError()

    def raise_for_status(self):                                                 # Raise exception if error status
        raise NotImplementedError()

    @property
    def content(self) -> bytes:                                                 # Raw response content
        raise NotImplementedError()