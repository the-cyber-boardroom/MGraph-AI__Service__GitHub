from fastapi                                                            import FastAPI
from osbot_fast_api.api.Fast_API                                        import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid   import Random_Guid
from osbot_utils.utils.Env                                              import set_env
from starlette.testclient                                               import TestClient
from mgraph_ai_service_github.config                                    import ENV_VAR__SERVICE__AUTH__PUBLIC_KEY, ENV_VAR__SERVICE__AUTH__PRIVATE_KEY
from mgraph_ai_service_github.fast_api.GitHub__Service__Fast_API        import GitHub__Service__Fast_API
from mgraph_ai_service_github.service.encryption.NaCl__Key_Management   import NaCl__Key_Management

TEST_API_KEY__NAME = 'key-used-in-pytest'
TEST_API_KEY__VALUE = Random_Guid()

class GitHub__Service__Fast_API__Test_Objs(Type_Safe):
    fast_api        : GitHub__Service__Fast_API     = None
    fast_api__app   : FastAPI               = None
    fast_api__client: TestClient            = None
    setup_completed : bool                  = False

github_service_fast_api_test_objs = GitHub__Service__Fast_API__Test_Objs()

def setup__github_service_fast_api_test_objs():
        with github_service_fast_api_test_objs as _:
            if github_service_fast_api_test_objs.setup_completed is False:
                _.nacl_keys        = create_and_set_nacl_keys()                     # note: this needs to happen first so that the nacl keys are set, before the routes are set
                _.fast_api         = GitHub__Service__Fast_API().setup()
                _.fast_api__app    = _.fast_api.app()
                _.fast_api__client = _.fast_api.client()
                _.setup_completed  = True

                set_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME , TEST_API_KEY__NAME)
                set_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, TEST_API_KEY__VALUE)
        return github_service_fast_api_test_objs

def create_and_set_nacl_keys():                                                         # Generate and set NaCl keys as environment variables
    nacl_manager = NaCl__Key_Management()
    nacl_keys    = nacl_manager.generate_nacl_keys()

    set_env(ENV_VAR__SERVICE__AUTH__PUBLIC_KEY , nacl_keys.public_key )
    set_env(ENV_VAR__SERVICE__AUTH__PRIVATE_KEY, nacl_keys.private_key)
    return nacl_keys
