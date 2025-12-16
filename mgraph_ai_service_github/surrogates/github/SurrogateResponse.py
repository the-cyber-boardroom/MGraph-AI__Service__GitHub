from typing import Dict, Any


class SurrogateResponse:                                                        # Wraps TestClient response to match requests.Response interface

    def __init__(self, response):
        self._response    = response
        self.status_code  = response.status_code
        self.content      = response.content
        self.text         = response.text
        self.headers      = dict(response.headers)

    def json(self) -> Dict[str, Any]:                                           # Parse JSON response
        return self._response.json()

    def raise_for_status(self):                                                 # Raise exception for error status codes
        if self.status_code >= 400:
            raise Exception(f"HTTP Error {self.status_code}: {self.text}")
