import requests
from osbot_utils.decorators.methods.cache_on_self                                          import cache_on_self
from mgraph_ai_service_github.service.github.session.Requests__Session                     import Requests__Session
from mgraph_ai_service_github.service.github.session.Requests__Session__Response           import Requests__Session__Response
from mgraph_ai_service_github.service.github.session.Requests__Session__Response__Requests import Requests__Session__Response__Requests


class Requests__Session__Github(Requests__Session):                             # Real GitHub API session using requests
    api_token : str = None

    @property
    def headers(self) -> dict:
        return self.requests_session().headers

    @cache_on_self
    def requests_session(self) -> requests.Session:                             # Create and cache requests.Session
        if self.api_token is None:
            raise ValueError('GitHub Access Token not setup')
        session = requests.Session()
        session.headers.update({ 'Authorization'        : f'token {self.api_token}'       ,
                                 'Accept'               : 'application/vnd.github.v3+json',
                                 'X-GitHub-Api-Version' : '2022-11-28'                    })
        return session

    def get(self, url: str, **kwargs) -> Requests__Session__Response:
        response = self.requests_session().get(url, **kwargs)
        return Requests__Session__Response__Requests(response)

    def put(self, url: str, **kwargs) -> Requests__Session__Response:
        response = self.requests_session().put(url, **kwargs)
        return Requests__Session__Response__Requests(response)

    def delete(self, url: str, **kwargs) -> Requests__Session__Response:
        response = self.requests_session().delete(url, **kwargs)
        return Requests__Session__Response__Requests(response)

    def post(self, url: str, **kwargs) -> Requests__Session__Response:
        response = self.requests_session().post(url, **kwargs)
        return Requests__Session__Response__Requests(response)