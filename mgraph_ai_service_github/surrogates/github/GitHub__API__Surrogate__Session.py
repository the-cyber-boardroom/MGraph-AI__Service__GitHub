from typing                                                         import Dict, Any
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from starlette.testclient                                           import TestClient
from mgraph_ai_service_github.surrogates.github.HeadersProxy        import HeadersProxy
from mgraph_ai_service_github.surrogates.github.SurrogateResponse   import SurrogateResponse


class GitHub__API__Surrogate__Session(Type_Safe):                               # requests.Session-compatible wrapper around TestClient
    
    test_client : TestClient
    _headers    : Dict[str, str]
    _base_url   : str             = 'https://api.github.com'                    # URL to strip from requests

    @property
    def headers(self) -> HeadersProxy:                                          # Return headers proxy supporting .update()
        return HeadersProxy(self)
    
    def _convert_url_to_path(self, url: str) -> str:                            # Strip base URL to get path for TestClient
        if url.startswith(self._base_url):
            return url[len(self._base_url):]
        if url.startswith('http://') or url.startswith('https://'):
            # Extract path from full URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.path
        return url
    
    def _prepare_headers(self, kwargs: dict) -> dict:                           # Merge instance headers with request headers
        request_headers = dict(self._headers)                                   # Copy instance headers
        if 'headers' in kwargs:
            request_headers.update(kwargs['headers'])
        return request_headers
    
    def get(self, url: str, **kwargs) -> 'SurrogateResponse':                   # Execute GET request via TestClient
        path    = self._convert_url_to_path(url)
        headers = self._prepare_headers(kwargs)
        
        response = self.test_client.get(path, headers=headers)
        return SurrogateResponse(response)
    
    def put(self, url: str, json: dict = None, **kwargs) -> 'SurrogateResponse': # Execute PUT request via TestClient
        path    = self._convert_url_to_path(url)
        headers = self._prepare_headers(kwargs)
        
        response = self.test_client.put(path, json=json, headers=headers)
        return SurrogateResponse(response)
    
    def delete(self, url: str, **kwargs) -> 'SurrogateResponse':                # Execute DELETE request via TestClient
        path    = self._convert_url_to_path(url)
        headers = self._prepare_headers(kwargs)
        
        response = self.test_client.delete(path, headers=headers)
        return SurrogateResponse(response)
    
    def post(self, url: str, json: dict = None, **kwargs) -> 'SurrogateResponse': # Execute POST request via TestClient
        path    = self._convert_url_to_path(url)
        headers = self._prepare_headers(kwargs)
        
        response = self.test_client.post(path, json=json, headers=headers)
        return SurrogateResponse(response)


