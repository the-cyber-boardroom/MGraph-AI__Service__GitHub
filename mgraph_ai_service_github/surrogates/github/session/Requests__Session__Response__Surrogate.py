from typing                                                                      import Dict, Any
from httpx                                                                       import Response
from mgraph_ai_service_github.service.github.session.Requests__Session__Response import Requests__Session__Response


class Requests__Session__Response__Surrogate(Requests__Session__Response):      # Wraps TestClient response
    _response : Response = None

    def __init__(self, response, **kwargs):
        super().__init__(**kwargs)
        self._response   = response
        self.status_code = response.status_code

    def json(self) -> Dict[str, Any]:
        return self._response.json()

    def raise_for_status(self):
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"{self.status_code} Error", response=self._response)

    @property
    def content(self) -> bytes:
        return self._response.content


