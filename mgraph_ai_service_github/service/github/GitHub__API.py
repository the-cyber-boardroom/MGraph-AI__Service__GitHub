import requests
from typing                                         import Dict, Optional, Any

from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_utils.utils.Env                          import get_env
from requests                                       import Session


class GitHub__API(Type_Safe):
    api_token  : str = None
    api_url    : str = 'https://api.github.com'    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_token:
            self.api_token = get_env('GIT_HUB__ACCESS_TOKEN')
    
    @cache_on_self
    def session(self) -> Session:
        if self.api_token is None:
            raise ValueError('GitHub Access Token not setup')
        session = requests.Session()               # Initialize session for connection reuse
        session.headers.update({ 'Authorization'        : f'token {self.api_token}'       ,
                                 'Accept'               : 'application/vnd.github.v3+json',
                                 'X-GitHub-Api-Version' : '2022-11-28'                    })
        return session

    def get(self, endpoint : str                                                   # API endpoint path
             ) -> Dict:                                                            # Returns JSON response

        url      = f"{self.api_url}{endpoint}"
        response = self.session().get(url)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint : str              ,                                     # API endpoint path
                  data     : Dict[str, Any]                                         # Data to send
             ) -> Optional[Dict]:                                                   # Returns JSON response if any

        url      = f"{self.api_url}{endpoint}"
        response = self.session().put(url, json=data)
        response.raise_for_status()

        if response.content:
            return response.json()
        return None

    def delete(self, endpoint : str                                                 # API endpoint path
                ) -> bool:                                                          # Returns True if successful

        url      = f"{self.api_url}{endpoint}"
        response = self.session().delete(url)
        response.raise_for_status()
        return response.status_code == 204
