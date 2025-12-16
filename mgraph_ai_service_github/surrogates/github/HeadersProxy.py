from typing import Dict


class HeadersProxy:                                                             # Proxy to support session.headers.update() pattern

    def __init__(self, session):                                                # can't use 'GitHub__API__Surrogate__Session' due to circular dependency
        self._session = session

    def update(self, headers: Dict[str, str]):                                  # Update session headers
        self._session._headers.update(headers)

    def __setitem__(self, key: str, value: str):                                # Support direct assignment
        self._session._headers[key] = value

    def __getitem__(self, key: str) -> str:                                     # Support direct access
        return self._session._headers[key]

    def get(self, key: str, default: str = None) -> str:                        # Support .get()
        return self._session._headers.get(key, default)

