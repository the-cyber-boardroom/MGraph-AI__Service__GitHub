from unittest                                                               import TestCase
from osbot_utils.utils.Env                                                  import load_dotenv, get_env, set_env
from mgraph_ai_service_github.config                                        import ENV_VAR__SERVICE__AUTH__PUBLIC_KEY, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management       import NaCl__Key_Management
from tests.unit.GitHub__Service__Fast_API__Test_Objs                        import setup__github_service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Auth__client__with_github_pat(TestCase):                                     # Tests requiring real GitHub PAT

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.github_pat = get_env('GIT_HUB__ACCESS_TOKEN', '')
        if not cls.github_pat:
            return                                                                              # Skip setup if no PAT

        cls.create_and_set_keys()
        with setup__github_service_fast_api_test_objs() as _:
            cls.test_objs = _
            cls.client    = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    # todo: refactor this to setup__github_service_fast_api_test_objs since we need to do this on multiple test files
    @classmethod
    def create_and_set_keys(cls):
        cls.nacl_manager = NaCl__Key_Management()
        cls.nacl_keys    = cls.nacl_manager.generate_nacl_keys()

        set_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY , cls.nacl_keys.public_key )
        set_env(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY, cls.nacl_keys.private_key)

    def setUp(self):
        if not self.github_pat:
            self.skipTest("GIT_HUB__ACCESS_TOKEN not set")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Full Flow Tests with Real GitHub PAT
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__auth_token_create__success(self):                                                 # Test POST /auth/token-create with real PAT
        response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
        result   = response.json()

        assert response.status_code        == 200
        assert result.get('success')       is True
        assert result.get('encrypted_pat') is not None
        assert result.get('user')          is not None
        assert result.get('user')['login'] is not None
        assert result.get('user')['id']    is not None
        assert result.get('instructions')  is not None

        self.__class__.encrypted_pat = result.get('encrypted_pat')

    def test__auth_token_validate__success(self):                                               # Test POST /auth/token-validate with real encrypted PAT
        if not hasattr(self.__class__, 'encrypted_pat'):
            create_response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
            create_result   = create_response.json()
            if not create_result.get('success'):
                self.skipTest(f"token-create failed: {create_result.get('error')}")
            self.__class__.encrypted_pat = create_result.get('encrypted_pat')

        response = self.client.post('/auth/token-validate', headers={'X-OSBot-GitHub-PAT': self.encrypted_pat})
        result   = response.json()

        assert response.status_code                  == 200
        assert result.get('success')                 is True
        assert result.get('user')                    is not None
        assert result.get('user')['login']           is not None
        assert result.get('rate_limit')              is not None
        assert result.get('rate_limit')['limit']     is not None
        assert result.get('rate_limit')['remaining'] is not None

    def test__auth_test__success(self):                                                         # Test GET /auth/test with real encrypted PAT
        if not hasattr(self.__class__, 'encrypted_pat'):
            create_response = self.client.post('/auth/token-create', headers={'X-GitHub-PAT': self.github_pat})
            create_result   = create_response.json()
            if not create_result.get('success'):
                self.skipTest(f"token-create failed: {create_result.get('error')}")
            self.__class__.encrypted_pat = create_result.get('encrypted_pat')

        response = self.client.get('/auth/test', headers={'X-OSBot-GitHub-PAT': self.encrypted_pat})
        result   = response.json()

        assert response.status_code              == 200
        assert result.get('success')             is True
        assert result.get('user')['login']       is not None
        assert result.get('rate_limit')['limit'] is not None