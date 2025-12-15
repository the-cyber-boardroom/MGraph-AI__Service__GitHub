import pytest
from unittest                                                                               import TestCase
from fastapi                                                                                import Response
from osbot_fast_api.api.routes.Fast_API__Routes                                             import Fast_API__Routes
from osbot_fast_api_serverless.utils.testing.skip_tests import skip__if_not__in_github_actions
from osbot_utils.helpers.duration.decorators.print_duration                                 import print_duration
from osbot_utils.testing.__                                                                 import __, __SKIP__
from osbot_utils.type_safe.Type_Safe                                                        import Type_Safe
from osbot_utils.utils.Env                                                                  import get_env, load_dotenv
from osbot_utils.utils.Objects                                                              import base_classes
from mgraph_ai_service_github.config                                                        import ENV_VAR__GIT_HUB__ACCESS_TOKEN, ENV_VAR__TESTS__GITHUB__REPO_OWNER, ENV_VAR__TESTS__GITHUB__REPO_NAME
from mgraph_ai_service_github.fast_api.dependencies.GitHub__API__From__Header               import GitHub__API__From__Header
from mgraph_ai_service_github.fast_api.routes.Routes__GitHub__Secrets__Org                  import Routes__GitHub__Secrets__Org, TAG__ROUTES_GITHUB_SECRETS_ORG, ROUTES_PATHS__GITHUB_SECRETS_ORG
from mgraph_ai_service_github.schemas.base.Enum__HTTP__Status                               import Enum__HTTP__Status
from mgraph_ai_service_github.schemas.base.Enum__Error__Type                                import Enum__Error__Type
from mgraph_ai_service_github.schemas.encryption.Enum__Encryption_Type                      import Enum__Encryption_Type
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Request                import Schema__Encryption__Request
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Request__Org__Secrets__List import Schema__GitHub__Request__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secrets__List import Schema__GitHub__Data__Request__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Response__Org__Secrets__List import Schema__GitHub__Response__Org__Secrets__List
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Request__Org__Secret__Operations import (
    Schema__GitHub__Request__Org__Secret__Get    ,
    Schema__GitHub__Request__Org__Secret__Create ,
    Schema__GitHub__Request__Org__Secret__Update ,
    Schema__GitHub__Request__Org__Secret__Delete )
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Get import Schema__GitHub__Data__Request__Org__Secret__Get
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Create import Schema__GitHub__Data__Request__Org__Secret__Create
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Data__Request__Org__Secret__Delete import Schema__GitHub__Data__Request__Org__Secret__Delete
from mgraph_ai_service_github.schemas.github.secrets.Schema__GitHub__Response__Org__Secret__Operations import (
    Schema__GitHub__Response__Org__Secret__Get    ,
    Schema__GitHub__Response__Org__Secret__Create ,
    Schema__GitHub__Response__Org__Secret__Update ,
    Schema__GitHub__Response__Org__Secret__Delete )
from mgraph_ai_service_github.service.auth.Service__Auth                                    import Service__Auth
from mgraph_ai_service_github.service.encryption.Service__Encryption                        import Service__Encryption
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management                       import NaCl__Key_Management
from mgraph_ai_service_github.utils.testing.Create_GitHub_Test_Data                         import Create_GitHub_Test_Data, TESTING__ORG__SECRETS__NAMES


class test_Routes__GitHub__Secrets__Org(TestCase):

    @classmethod
    def setUpClass(cls):                                                                        # Setup test configuration
        skip__if_not__in_github_actions()
        cls.nacl_manager       = NaCl__Key_Management()
        cls.test_keys          = cls.nacl_manager.generate_nacl_keys()
        cls.service_auth       = Service__Auth               (private_key_hex = cls.test_keys.private_key ,
                                                              public_key_hex  = cls.test_keys.public_key  )
        cls.service_encryption = Service__Encryption         (private_key_hex = cls.test_keys.private_key ,
                                                              public_key_hex  = cls.test_keys.public_key  )
        cls.github_api_factory = GitHub__API__From__Header   (service_auth = cls.service_auth)
        cls.routes             = Routes__GitHub__Secrets__Org(github_api_factory = cls.github_api_factory ,
                                                              service_encryption = cls.service_encryption )

        load_dotenv()
        cls.github_pat = get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN     )
        cls.repo_owner = get_env(ENV_VAR__TESTS__GITHUB__REPO_OWNER)                            # Used as org name
        cls.repo_name  = get_env(ENV_VAR__TESTS__GITHUB__REPO_NAME )
        if not cls.github_pat or not cls.repo_owner or not cls.repo_name:
            pytest.skip('Skipping tests because GitHub Access Token or target repo are not available')

        cls.encrypt_request = Schema__Encryption__Request(value           = cls.github_pat            ,
                                                          encryption_type = Enum__Encryption_Type.TEXT)
        cls.encrypted_pat   = cls.service_encryption.encrypt(cls.encrypt_request).encrypted

        cls.create_test_data = Create_GitHub_Test_Data()
        # if cls.create_test_data.setup__env_vars_defined_ok() is False:
        #     pytest.skip("Skipping test because env vars not defined")
        # if cls.create_test_data.has_org_admin_access() is False:
        #     pytest.skip("Skipping org secrets tests - no org admin access")
        # if cls.create_test_data.create_org_secrets() is False:
        #     pytest.skip("Skipping test because org secrets could not be created")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Initialization Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                                     # Test auto-initialization
        with self.routes as _:
            assert type(_)                    is Routes__GitHub__Secrets__Org
            assert base_classes(_)            == [Fast_API__Routes, Type_Safe, object]
            assert _.tag                      == TAG__ROUTES_GITHUB_SECRETS_ORG
            assert type(_.github_api_factory) is GitHub__API__From__Header
            assert type(_.service_encryption) is Service__Encryption

    def test__routes_paths(self):                                                               # Test route paths constant
        assert ROUTES_PATHS__GITHUB_SECRETS_ORG == [ '/github-secrets-org/list'   ,
                                                     '/github-secrets-org/get'    ,
                                                     '/github-secrets-org/create' ,
                                                     '/github-secrets-org/update' ,
                                                     '/github-secrets-org/delete' ]
        assert len(ROUTES_PATHS__GITHUB_SECRETS_ORG) == 5

    # ═══════════════════════════════════════════════════════════════════════════════
    # list Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__list__success(self):                                                              # Test list returns organization secrets
        request_data = Schema__GitHub__Data__Request__Org__Secrets__List(org = self.repo_owner)
        request  = Schema__GitHub__Request__Org__Secrets__List(encrypted_pat = self.encrypted_pat ,
                                                               request_data  = request_data       )
        response = Response()

        with self.routes as _:
            with print_duration():
                result = _.list(request, response)

            assert type(result)                        is Schema__GitHub__Response__Org__Secrets__List
            assert result.response_context.success     is True
            assert result.response_context.status_code == Enum__HTTP__Status.OK_200
            assert result.response_context.duration    > 0
            assert len(result.response_data.secrets)   >= 2                                     # At least our test secrets

            secret_names = [s.name for s in result.response_data.secrets]
            for expected_name in TESTING__ORG__SECRETS__NAMES:
                assert expected_name in secret_names                                            # Test secrets should be present

            assert result.response_context.obj() == __(rate_limit  = __(limit     = 5000     ,
                                                                        remaining = __SKIP__ ,
                                                                        reset     = __SKIP__ ,
                                                                        used      = __SKIP__ ),
                                                       timestamp   = __SKIP__ ,
                                                       messages    = []       ,
                                                       errors      = []       ,
                                                       success     = True     ,
                                                       status_code = 200      ,
                                                       duration    = __SKIP__ ,
                                                       error_type  = 'none'   )

    def test__list__invalid_org(self):                                                          # Test list with nonexistent org
        request_data = Schema__GitHub__Data__Request__Org__Secrets__List(org = 'nonexistent-org-xyz-12345')
        request  = Schema__GitHub__Request__Org__Secrets__List(encrypted_pat = self.encrypted_pat ,
                                                               request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.list(request, response)

            assert result.response_context.success     is False
            assert result.response_context.status_code in [Enum__HTTP__Status.NOT_FOUND_404, Enum__HTTP__Status.FORBIDDEN_403]

    # ═══════════════════════════════════════════════════════════════════════════════
    # get Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__get__success(self):                                                               # Test get returns org secret metadata
        secret_name  = TESTING__ORG__SECRETS__NAMES[0]
        request_data = Schema__GitHub__Data__Request__Org__Secret__Get(org         = self.repo_owner ,
                                                                       secret_name = secret_name     )
        request  = Schema__GitHub__Request__Org__Secret__Get(encrypted_pat = self.encrypted_pat ,
                                                             request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.get(request, response)

            assert type(result)                           is Schema__GitHub__Response__Org__Secret__Get
            assert result.response_context.success        is True
            assert result.response_context.status_code    == Enum__HTTP__Status.OK_200
            assert result.response_data.secret.name       == secret_name
            assert result.response_data.secret.visibility is not None

    def test__get__not_found(self):                                                             # Test get with nonexistent org secret
        request_data = Schema__GitHub__Data__Request__Org__Secret__Get(org         = self.repo_owner          ,
                                                                       secret_name = 'NONEXISTENT_SECRET_XYZ' )
        request  = Schema__GitHub__Request__Org__Secret__Get(encrypted_pat = self.encrypted_pat ,
                                                             request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.get(request, response)

            assert result.response_context.success     is False
            assert result.response_context.status_code == Enum__HTTP__Status.NOT_FOUND_404
            assert result.response_context.error_type  == Enum__Error__Type.NOT_FOUND

    # ═══════════════════════════════════════════════════════════════════════════════
    # create Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__create__success(self):                                                            # Test create org secret successfully
        secret_name     = 'TEST_ORG_CREATE_TEMP'
        secret_value    = 'test_org_secret_value_123'
        encrypted_value = self.service_encryption.encrypt(
            Schema__Encryption__Request(value=secret_value, encryption_type=Enum__Encryption_Type.TEXT)).encrypted

        request_data = Schema__GitHub__Data__Request__Org__Secret__Create(org             = self.repo_owner ,
                                                                          secret_name     = secret_name     ,
                                                                          encrypted_value = encrypted_value ,
                                                                          visibility      = 'private'       )
        request  = Schema__GitHub__Request__Org__Secret__Create(encrypted_pat = self.encrypted_pat ,
                                                                request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.create(request, response)

            assert type(result)                        is Schema__GitHub__Response__Org__Secret__Create
            assert result.response_context.success     is True
            assert result.response_context.status_code == Enum__HTTP__Status.CREATED_201
            assert result.response_data.created        is True

        # Verify secret was created
        with self.create_test_data.github_secrets() as _:
            secret = _.get_org_secret(self.repo_owner, secret_name)
            assert secret is not None
            assert secret.get('name')       == secret_name
            assert secret.get('visibility') == 'private'

        # Cleanup: delete the created secret
        with self.create_test_data.github_secrets() as _:
            deleted = _.delete_org_secret(self.repo_owner, secret_name)
            assert deleted is True

        # Verify secret was deleted
        with self.create_test_data.github_secrets() as _:
            secret = _.get_org_secret(self.repo_owner, secret_name)
            assert secret is None

    def test__create__with_visibility_all(self):                                                # Test create org secret with visibility='all'
        secret_name     = 'TEST_ORG_VIS_ALL_TEMP'
        secret_value    = 'test_org_secret_all'
        encrypted_value = self.service_encryption.encrypt(
            Schema__Encryption__Request(value=secret_value, encryption_type=Enum__Encryption_Type.TEXT)).encrypted

        request_data = Schema__GitHub__Data__Request__Org__Secret__Create(org             = self.repo_owner ,
                                                                          secret_name     = secret_name     ,
                                                                          encrypted_value = encrypted_value ,
                                                                          visibility      = 'all'           )
        request  = Schema__GitHub__Request__Org__Secret__Create(encrypted_pat = self.encrypted_pat ,
                                                                request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.create(request, response)

            assert result.response_context.success     is True
            assert result.response_context.status_code == Enum__HTTP__Status.CREATED_201

        # Cleanup
        with self.create_test_data.github_secrets() as _:
            assert _.delete_org_secret(self.repo_owner, secret_name) is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # update Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__update__success(self):                                                            # Test update org secret successfully
        secret_name     = TESTING__ORG__SECRETS__NAMES[0]
        new_value       = 'updated_org_secret_value_456'
        encrypted_value = self.service_encryption.encrypt(
            Schema__Encryption__Request(value=new_value, encryption_type=Enum__Encryption_Type.TEXT)).encrypted

        request_data = Schema__GitHub__Data__Request__Org__Secret__Create(org             = self.repo_owner ,
                                                                          secret_name     = secret_name     ,
                                                                          encrypted_value = encrypted_value ,
                                                                          visibility      = 'private'       )
        request  = Schema__GitHub__Request__Org__Secret__Update(encrypted_pat = self.encrypted_pat ,
                                                                request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.update(request, response)

            assert type(result)                        is Schema__GitHub__Response__Org__Secret__Update
            assert result.response_context.success     is True
            assert result.response_context.status_code == Enum__HTTP__Status.OK_200
            assert result.response_data.updated        is True

    # ═══════════════════════════════════════════════════════════════════════════════
    # delete Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__delete__success(self):                                                            # Test delete org secret successfully
        # First create a secret to delete
        secret_name     = 'TEST_ORG_DELETE_TEMP'
        secret_value    = 'value_to_delete'
        encrypted_value = self.service_encryption.encrypt(
            Schema__Encryption__Request(value=secret_value, encryption_type=Enum__Encryption_Type.TEXT)).encrypted

        create_request_data = Schema__GitHub__Data__Request__Org__Secret__Create(org             = self.repo_owner ,
                                                                                 secret_name     = secret_name     ,
                                                                                 encrypted_value = encrypted_value ,
                                                                                 visibility      = 'private'       )
        create_request = Schema__GitHub__Request__Org__Secret__Create(encrypted_pat = self.encrypted_pat   ,
                                                                      request_data  = create_request_data  )
        self.routes.create(create_request, Response())

        # Now delete it
        delete_request_data = Schema__GitHub__Data__Request__Org__Secret__Delete(org         = self.repo_owner ,
                                                                                 secret_name = secret_name     )
        delete_request = Schema__GitHub__Request__Org__Secret__Delete(encrypted_pat = self.encrypted_pat   ,
                                                                      request_data  = delete_request_data  )
        response = Response()

        with self.routes as _:
            result = _.delete(delete_request, response)

            assert type(result)                        is Schema__GitHub__Response__Org__Secret__Delete
            assert result.response_context.success     is True
            assert result.response_context.status_code == Enum__HTTP__Status.OK_200
            assert result.response_data.deleted        is True

    def test__delete__not_found(self):                                                          # Test delete nonexistent org secret
        request_data = Schema__GitHub__Data__Request__Org__Secret__Delete(org         = self.repo_owner          ,
                                                                          secret_name = 'NONEXISTENT_DELETE_XYZ' )
        request  = Schema__GitHub__Request__Org__Secret__Delete(encrypted_pat = self.encrypted_pat ,
                                                                request_data  = request_data       )
        response = Response()

        with self.routes as _:
            result = _.delete(request, response)

            assert result.response_context.success     is False
            assert result.response_context.status_code == Enum__HTTP__Status.NOT_FOUND_404
            assert result.response_data.deleted        is False

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup_routes Tests
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__setup_routes(self):                                                               # Test setup_routes registers all routes
        routes = Routes__GitHub__Secrets__Org(github_api_factory = self.github_api_factory ,
                                              service_encryption = self.service_encryption )
        result = routes.setup_routes()

        assert result is None                                                                   # setup_routes doesn't return self