from typing                                                                    import Dict, Optional, Any, Callable, Type
from osbot_utils.decorators.methods.cache_on_self                              import cache_on_self
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.utils.Env                                                     import get_env
from mgraph_ai_service_github.service.github.session.Requests__Session         import Requests__Session
from mgraph_ai_service_github.service.github.session.Requests__Session__Github import Requests__Session__Github

# todo see if can do this in a better way
# Module-level session factory - can be swapped for testing
_session_factory: Callable[[str], Requests__Session] = None

def set_session_factory(factory: Callable[[str], Requests__Session]):           # Set custom session factory
    global _session_factory
    _session_factory = factory


def clear_session_factory():                                                    # Clear custom session factory
    global _session_factory
    _session_factory = None


class GitHub__API(Type_Safe):
    api_token : str = None
    api_url   : str = 'https://api.github.com'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_token:
            self.api_token = get_env('GIT_HUB__ACCESS_TOKEN')

    @cache_on_self
    def session(self) -> Requests__Session:                                     # Get session (real or surrogate)
        if _session_factory is not None:
            return _session_factory(self.api_token)
        return Requests__Session__Github(api_token=self.api_token)

    def get(self, endpoint : str                                                # API endpoint path
             ) -> Dict:                                                         # Returns JSON response
        url      = f"{self.api_url}{endpoint}"
        response = self.session().get(url)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint : str              ,                                 # API endpoint path
                  data     : Dict[str, Any]                                     # Data to send
             ) -> Optional[Dict]:                                               # Returns JSON response if any
        url      = f"{self.api_url}{endpoint}"
        response = self.session().put(url, json=data)
        response.raise_for_status()

        if response.content:
            return response.json()
        return None

    def delete(self, endpoint : str                                             # API endpoint path
                ) -> bool:                                                      # Returns True if successful
        url      = f"{self.api_url}{endpoint}"
        response = self.session().delete(url)
        response.raise_for_status()
        return response.status_code == 204