from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from mgraph_ai_service_github.service.github.session.Requests__Session__Response  import Requests__Session__Response


class Requests__Session(Type_Safe):                                           # Abstract base for HTTP session operations
    
    def get(self, url: str, **kwargs) -> Requests__Session__Response:         # GET request
        raise NotImplementedError()
    
    def put(self, url: str, **kwargs) -> Requests__Session__Response:         # PUT request
        raise NotImplementedError()
    
    def delete(self, url: str, **kwargs) -> Requests__Session__Response:      # DELETE request
        raise NotImplementedError()
    
    def post(self, url: str, **kwargs) -> Requests__Session__Response:        # POST request
        raise NotImplementedError()


