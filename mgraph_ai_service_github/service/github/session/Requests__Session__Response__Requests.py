from typing                                                                      import Dict, Any
from requests                                                                    import Response
from mgraph_ai_service_github.service.github.session.Requests__Session__Response import Requests__Session__Response


class Requests__Session__Response__Requests(Requests__Session__Response):       # Wraps requests.Response
    _response : Response = None                                                   # The actual requests.Response

    def __init__(self, response: Response, **kwargs):
        super().__init__(**kwargs)
        self._response   = response
        self.status_code = response.status_code

    def json(self) -> Dict[str, Any]:
        return self._response.json()

    def raise_for_status(self):
        self._response.raise_for_status()

    @property
    def content(self) -> bytes:
        return self._response.content


