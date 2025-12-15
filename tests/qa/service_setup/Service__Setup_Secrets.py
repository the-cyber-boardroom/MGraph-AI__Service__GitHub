from typing import List

from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.type_safe.type_safe_core.decorators.type_safe import type_safe
from osbot_utils.utils.Env                          import get_env, load_dotenv

from mgraph_ai_service_github.schemas.encryption.Safe_Str__Decrypted_Value import Safe_Str__Decrypted_Value
from mgraph_ai_service_github.service.github.GitHub__Secrets import GitHub__Secrets
from tests.qa                                       import service_setup
from osbot_utils.type_safe.Type_Safe                import Type_Safe
from osbot_utils.utils.Files                        import path_combine, file_exists

FILE__DOTENV__SETUP_SECRETS                    = '.setup-secrets.env'
ENV_NAME__SERVICE__SETUP__SECRETS__REPO_NAME   = "SERVICE__SETUP__SECRETS__REPO_NAME"
ENV_NAME__SERVICE__SETUP__SECRETS__REPO_OWNER  = "SERVICE__SETUP__SECRETS__REPO_OWNER"
ENV_NAME__GIT_HUB__ACCESS_TOKEN                = 'GIT_HUB__ACCESS_TOKEN'

# todo: see if we should move this to the main code base (under service or use-cases?)
class Service__Setup_Secrets(Type_Safe):

    # ═══════════════════════════════════════════════════════════════════════════════
    # support methods
    # ═══════════════════════════════════════════════════════════════════════════════

    @cache_on_self
    def api_token(self):
        return get_env(ENV_NAME__GIT_HUB__ACCESS_TOKEN)

    def dot_env_file(self):
        return path_combine(service_setup.path, FILE__DOTENV__SETUP_SECRETS)

    @cache_on_self
    def github_secrets(self):
        return GitHub__Secrets(repo_name = self.repo()      ,
                               api_token = self.api_token() )
    @cache_on_self
    def repo_name(self):
        return get_env(ENV_NAME__SERVICE__SETUP__SECRETS__REPO_NAME)

    @cache_on_self
    def repo_owner(self):
        return get_env(ENV_NAME__SERVICE__SETUP__SECRETS__REPO_OWNER)

    @cache_on_self
    def repo(self):
        return f'{self.repo_owner()}/{self.repo_name()}'

    def setup(self):
        dot_env_file = self.dot_env_file()
        if file_exists(dot_env_file):
            load_dotenv(dotenv_path=dot_env_file, override=True)
            if self.api_token():
                if self.repo_name() and self.repo_owner():
                    return True
        return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # main methods
    # ═══════════════════════════════════════════════════════════════════════════════


    @type_safe
    def current_secrets(self) -> List[Safe_Str__Decrypted_Value]:
        return self.github_secrets().list_secrets()

    @type_safe
    def secrets_to_configure(self):
        return []