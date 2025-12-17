from typing                                                                                     import Dict
from starlette.testclient                                                                       import TestClient
from mgraph_ai_service_github.service.github.session.Requests__Session                          import Requests__Session
from mgraph_ai_service_github.service.github.session.Requests__Session__Response                import Requests__Session__Response
from mgraph_ai_service_github.surrogates.github.session.Requests__Session__Response__Surrogate  import Requests__Session__Response__Surrogate


class Requests__Session__Github__Surrogate(Requests__Session):                  # Surrogate session using TestClient
    api_token   : str        = None
    test_client : TestClient = None

    @property
    def headers(self) -> dict:
        return {'Authorization'        : f'token {self.api_token}'       ,
                'Accept'               : 'application/vnd.github.v3+json',
                'X-GitHub-Api-Version' : '2022-11-28'                    }

    def _headers(self) -> Dict[str, str]:                                       # Build headers with current api_token
        return {'Authorization': f'token {self.api_token}'}

    def _path_from_url(self, url: str) -> str:                                  # Extract path from full URL
        if url.startswith('http'):
            from urllib.parse import urlparse
            return urlparse(url).path
        return url

    def get(self, url: str, **kwargs) -> Requests__Session__Response:
        path     = self._path_from_url(url)
        headers  = {**self._headers(), **kwargs.pop('headers', {})}
        response = self.test_client.get(path, headers=headers, **kwargs)
        return Requests__Session__Response__Surrogate(response)

    def put(self, url: str, **kwargs) -> Requests__Session__Response:
        path     = self._path_from_url(url)
        headers  = {**self._headers(), **kwargs.pop('headers', {})}
        response = self.test_client.put(path, headers=headers, **kwargs)
        return Requests__Session__Response__Surrogate(response)

    def delete(self, url: str, **kwargs) -> Requests__Session__Response:
        path     = self._path_from_url(url)
        headers  = {**self._headers(), **kwargs.pop('headers', {})}
        response = self.test_client.delete(path, headers=headers, **kwargs)
        return Requests__Session__Response__Surrogate(response)

    def post(self, url: str, **kwargs) -> Requests__Session__Response:
        path     = self._path_from_url(url)
        headers  = {**self._headers(), **kwargs.pop('headers', {})}
        response = self.test_client.post(path, headers=headers, **kwargs)
        return Requests__Session__Response__Surrogate(response)