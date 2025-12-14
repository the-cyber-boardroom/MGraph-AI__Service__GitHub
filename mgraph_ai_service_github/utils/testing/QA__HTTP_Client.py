import pytest
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url            import Safe_Str__Url
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text        import Safe_Str__Text
from osbot_utils.utils.Env                                                          import get_env, load_dotenv
from requests                                                                       import Session, Response

ENV_VAR__GIT_HUB__ACCESS_TOKEN  = 'GIT_HUB__ACCESS_TOKEN'
ENV_VAR__GIT_HUB__SERVICE__URL  = 'GIT_HUB__SERVICE__URL'
ENV_VAR__SERVICE__API_KEY__NAME = 'FAST_API__AUTH__API_KEY__NAME'
ENV_VAR__SERVICE__API_KEY__VALUE= 'FAST_API__AUTH__API_KEY__VALUE'

DEFAULT__SERVICE__URL           = 'https://github.dev.mgraph.ai'


class QA__HTTP_Client(Type_Safe):                                                   # HTTP client for QA tests against live server
    service_url    : Safe_Str__Url   = None
    api_key_name   : Safe_Str__Text  = None
    api_key_value  : Safe_Str__Text  = None
    github_pat     : Safe_Str__Text  = None
    session        : Session         = None
    timeout        : int             = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.session is None:
            self.session = Session()

    def auth_headers(self):                                                         # Headers with API key authentication
        if self.api_key_name and self.api_key_value:
            return {self.api_key_name: self.api_key_value}
        return {}

    def url_for(self, path: str) -> str:                                            # Build full URL for endpoint
        return f"{self.service_url}{path}"

    def get(self, path     : str           ,                                        # GET request with authentication
                  headers  : dict = None
            ) -> Response:
        request_headers = self.auth_headers()
        if headers:
            request_headers.update(headers)
        return self.session.get(url     = self.url_for(path) ,
                                headers = request_headers    ,
                                timeout = self.timeout       )

    def post(self, path    : str           ,                                        # POST request with authentication
                   json    : dict = None   ,
                   headers : dict = None
             ) -> Response:
        request_headers = self.auth_headers()
        if headers:
            request_headers.update(headers)
        return self.session.post(url     = self.url_for(path) ,
                                 json    = json               ,
                                 headers = request_headers    ,
                                 timeout = self.timeout       )


class QA__Test_Objs(Type_Safe):                                                     # Shared test objects for QA tests
    http_client     : QA__HTTP_Client = None
    setup_completed : bool            = False
    setup_error     : str             = None

qa_test_objs = QA__Test_Objs()                                                      # Singleton instance


def setup__qa_test_objs() -> QA__Test_Objs:                                         # Initialize QA test objects from environment
    load_dotenv()

    with qa_test_objs as _:
        if _.setup_completed:
            return _

        service_url   = get_env(ENV_VAR__GIT_HUB__SERVICE__URL , DEFAULT__SERVICE__URL)
        api_key_name  = get_env(ENV_VAR__SERVICE__API_KEY__NAME , '')
        api_key_value = get_env(ENV_VAR__SERVICE__API_KEY__VALUE, '')
        github_pat    = get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN  , '')

        _.http_client = QA__HTTP_Client(service_url   = Safe_Str__Url (service_url  ) ,
                                        api_key_name  = Safe_Str__Text(api_key_name ) if api_key_name  else None,
                                        api_key_value = Safe_Str__Text(api_key_value) if api_key_value else None,
                                        github_pat    = Safe_Str__Text(github_pat   ) if github_pat    else None)
        _.setup_completed = True

    return qa_test_objs


def skip_if_no_service_url():                                                       # Skip decorator if service URL not configured
    load_dotenv()
    service_url = get_env(ENV_VAR__GIT_HUB__SERVICE__URL, DEFAULT__SERVICE__URL)
    if not service_url:
        pytest.skip(f"QA tests require {ENV_VAR__GIT_HUB__SERVICE__URL} to be set")


def skip_if_no_github_pat():                                                        # Skip decorator if GitHub PAT not configured
    load_dotenv()
    github_pat = get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN, '')
    if not github_pat:
        pytest.skip(f"GitHub PAT tests require {ENV_VAR__GIT_HUB__ACCESS_TOKEN} to be set")


def skip_if_no_api_key():                                                           # Skip decorator if API key not configured
    load_dotenv()
    api_key_name  = get_env(ENV_VAR__SERVICE__API_KEY__NAME , '')
    api_key_value = get_env(ENV_VAR__SERVICE__API_KEY__VALUE, '')
    if not api_key_name or not api_key_value:
        pytest.skip(f"API key tests require {ENV_VAR__SERVICE__API_KEY__NAME} and {ENV_VAR__SERVICE__API_KEY__VALUE} to be set")