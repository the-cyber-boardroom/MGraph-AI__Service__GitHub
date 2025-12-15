from unittest                                               import TestCase
from osbot_fast_api_serverless.utils.testing.skip_tests     import skip__if_not__in_github_actions
from requests.exceptions                                    import HTTPError
from osbot_utils.utils.Env                                  import get_env,load_dotenv
from mgraph_ai_service_github.config                        import DEPLOY__GITHUB__REPO__OWNER, DEPLOY__GITHUB__REPO__NAME
from mgraph_ai_service_github.service.github.GitHub__API    import GitHub__API

class test_GitHub__API(TestCase):

    @classmethod
    def setUpClass(cls):                                                                        # Setup test configuration
        skip__if_not__in_github_actions()
        cls.test_repo_owner = DEPLOY__GITHUB__REPO__OWNER     # Replace with your org/user
        cls.test_repo_name  = DEPLOY__GITHUB__REPO__NAME      # Replace with your test repo
        cls.test_repo       = f'{cls.test_repo_owner}/{cls.test_repo_name}'

    def setUp(self):                                                                            # Initialize test fixtures
        load_dotenv()
        self.api_token  = get_env('GIT_HUB__ACCESS_TOKEN')
        self.api_url    = 'https://api.github.com'
        self.github_api = GitHub__API(api_token = self.api_token)

    def test__init__(self):                                                       # Test basic initialization
        assert type(self.github_api)        is GitHub__API
        assert self.github_api.api_token    == self.api_token
        assert self.github_api.api_url      == self.api_url
        assert self.api_token is not None

    def test__init__with_env_token(self):                                        # Test initialization with env token
        github_api = GitHub__API()
        assert github_api.api_token == self.api_token
        assert github_api.api_url   == 'https://api.github.com'

    def test__init__session_headers(self):                                       # Test session headers configuration
        expected_headers = { 'Authorization'        : f'token {self.api_token}'       ,
                            'Accept'                : 'application/vnd.github.v3+json' ,
                            'X-GitHub-Api-Version' : '2022-11-28'                     }

        for header, value in expected_headers.items():
            assert self.github_api.session().headers[header] == value

    def test_get__user(self):                                                    # Test GET request for authenticated user
        endpoint = '/user'
        result   = self.github_api.get(endpoint)

        assert type(result)         is dict
        assert 'login'              in result
        assert 'id'                 in result
        assert 'type'               in result
        assert result['type']       == 'User'

    def test_get__repo(self):                                                    # Test GET request for repository
        endpoint = f'/repos/{self.test_repo}'
        result   = self.github_api.get(endpoint)

        assert type(result)         is dict
        assert 'name'               in result
        assert 'full_name'          in result
        assert 'owner'              in result
        assert result['full_name']  == self.test_repo

    def test_get__repo_secrets(self):                                           # Test GET request for repository secrets
        endpoint = f'/repos/{self.test_repo}/actions/secrets'
        result   = self.github_api.get(endpoint)

        assert type(result)         is dict
        assert 'total_count'        in result
        assert 'secrets'            in result
        assert type(result['secrets']) is list

    def test_get__invalid_endpoint(self):                                       # Test GET request with invalid endpoint
        endpoint = '/repos/nonexistent-owner/nonexistent-repo'

        with self.assertRaises(HTTPError) as context:
            self.github_api.get(endpoint)

        assert '404' in str(context.exception)

    def test_get__rate_limit(self):                                            # Test GET request for rate limit info
        endpoint = '/rate_limit'
        result   = self.github_api.get(endpoint)

        assert type(result)              is dict
        assert 'rate'                    in result
        assert 'limit'                   in result['rate']
        assert 'remaining'               in result['rate']
        assert type(result['rate']['limit'])     is int
        assert type(result['rate']['remaining']) is int

    def test_put__create_update_secret(self):                                  # Test PUT request to create/update secret
        import base64
        from nacl import encoding, public

        # Get public key for encryption
        endpoint        = f'/repos/{self.test_repo}/actions/secrets/public-key'
        public_key_data = self.github_api.get(endpoint)

        # Encrypt a test value
        public_key_bytes = base64.b64decode(public_key_data['key'])
        sealed_box       = public.SealedBox(public.PublicKey(public_key_bytes))
        encrypted        = sealed_box.encrypt('test_secret_value'.encode('utf-8'))
        encrypted_value  = base64.b64encode(encrypted).decode('utf-8')

        # Create/update the secret
        secret_name = 'TEST_SECRET_FROM_API_TEST'
        endpoint    = f'/repos/{self.test_repo}/actions/secrets/{secret_name}'
        data        = { 'encrypted_value' : encrypted_value               ,
                       'key_id'          : public_key_data['key_id']     }

        result__create = self.github_api.put(endpoint, data)
        assert result__create == {}
        result__delete = self.github_api.delete(endpoint)
        assert result__delete is True


    def test_put__invalid_data(self):                                          # Test PUT request with invalid data
        endpoint = f'/repos/{self.test_repo}/actions/secrets/INVALID_SECRET'
        data     = {'invalid_field': 'invalid_value'}

        with self.assertRaises(HTTPError) as context:
            self.github_api.put(endpoint, data)

        assert '422' in str(context.exception) or '400' in str(context.exception)

    # already tested in test_put__create_update_secret
    # def test_delete__secret(self):                                             # Test DELETE request for secret
    #     import base64
    #     from nacl import encoding, public
    #
    #     # First create a secret to delete
    #     endpoint        = f'/repos/{self.test_repo}/actions/secrets/public-key'
    #     public_key_data = self.github_api.get(endpoint)
    #
    #     public_key_bytes = base64.b64decode(public_key_data['key'])
    #     sealed_box       = public.SealedBox(public.PublicKey(public_key_bytes))
    #     encrypted        = sealed_box.encrypt('temp_value'.encode('utf-8'))
    #     encrypted_value  = base64.b64encode(encrypted).decode('utf-8')
    #
    #     secret_name = 'TEMP_SECRET_TO_DELETE'
    #     endpoint    = f'/repos/{self.test_repo}/actions/secrets/{secret_name}'
    #     data        = { 'encrypted_value' : encrypted_value               ,
    #                    'key_id'          : public_key_data['key_id']     }
    #
    #     self.github_api.put(endpoint, data)
    #
    #     # Now delete it
    #     result = self.github_api.delete(endpoint)
    #
    #     assert result is True

    def test_delete__nonexistent_secret(self):                                 # Test DELETE for nonexistent secret
        endpoint = f'/repos/{self.test_repo}/actions/secrets/NONEXISTENT_SECRET_XYZ'

        with self.assertRaises(HTTPError) as context:
            self.github_api.delete(endpoint)

        assert '404' in str(context.exception)

    def test_custom_api_url(self):                                             # Test with custom API URL
        custom_url = 'https://api.github.com'  # Using same URL for test
        github_api = GitHub__API(api_token = self.api_token ,
                                       api_url   = custom_url     )

        assert github_api.api_url == custom_url

        # Verify it works
        result = github_api.get('/user')
        assert 'login' in result

    def test_session_reuse(self):                                              # Test that session is reused across calls
        endpoint = '/user'

        # Make multiple calls
        result1 = self.github_api.get(endpoint)
        result2 = self.github_api.get(endpoint)
        result3 = self.github_api.get(endpoint)

        # All should return same user info
        assert result1['id'] == result2['id'] == result3['id']
        assert result1['login'] == result2['login'] == result3['login']

    def test_get__with_pagination(self):                                       # Test GET with paginated results
        endpoint = f'/repos/{self.test_repo}/issues?state=all&per_page=1'
        result   = self.github_api.get(endpoint)

        assert type(result) is list
        assert len(result) <= 1  # Should respect per_page parameter

    def test_get__branches(self):                                              # Test GET request for repository branches
        endpoint = f'/repos/{self.test_repo}/branches'
        result   = self.github_api.get(endpoint)

        assert type(result) is list
        if len(result) > 0:  # If repo has branches
            assert 'name'       in result[0]
            assert 'commit'     in result[0]
            assert 'protected'  in result[0]

    def test_get__commits(self):                                               # Test GET request for repository commits
        endpoint = f'/repos/{self.test_repo}/commits?per_page=5'
        result   = self.github_api.get(endpoint)

        assert type(result) is list
        if len(result) > 0:  # If repo has commits
            assert 'sha'        in result[0]
            assert 'commit'     in result[0]
            assert 'author'     in result[0]['commit']
            assert 'message'    in result[0]['commit']