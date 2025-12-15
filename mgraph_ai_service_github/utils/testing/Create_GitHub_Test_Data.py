from osbot_utils.decorators.methods.cache_on_self               import cache_on_self
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_utils.utils.Env                                      import get_env
from osbot_utils.utils.Misc                                     import random_text
from mgraph_ai_service_github.config                            import ENV_VAR__TESTS__GITHUB__REPO_OWNER, ENV_VAR__TESTS__GITHUB__REPO_NAME, ENV_VAR__GIT_HUB__ACCESS_TOKEN
from mgraph_ai_service_github.service.github.GitHub__API        import GitHub__API
from mgraph_ai_service_github.service.github.GitHub__Secrets    import GitHub__Secrets

# Test secret names for each scope
TESTING__REPO__SECRETS__NAMES = ['REPO_SECRET_ONE', 'REPO_SECRET_TWO']
TESTING__ENV__SECRETS__NAMES  = ['ENV_SECRET_ONE' , 'ENV_SECRET_TWO' ]
TESTING__ORG__SECRETS__NAMES  = ['ORG_SECRET_ONE' , 'ORG_SECRET_TWO' ]
TESTING__ENVIRONMENT__NAME    = 'testing'                                       # GitHub environment name for env secrets


class Create_GitHub_Test_Data(Type_Safe):

    # ═══════════════════════════════════════════════════════════════════════════════
    # setup methods
    # ═══════════════════════════════════════════════════════════════════════════════

    @cache_on_self
    def github_api(self) -> GitHub__API:
        return GitHub__API(api_token=self.api_token())

    @cache_on_self
    def github_secrets(self) -> GitHub__Secrets:
        repo_owner_and_name = f"{self.repo_owner()}/{self.repo_name()}"
        return GitHub__Secrets(api_token = self.api_token()      ,
                               repo_name = repo_owner_and_name   )

    @cache_on_self
    def repo_name(self):
        return get_env(ENV_VAR__TESTS__GITHUB__REPO_NAME)

    @cache_on_self
    def repo_owner(self):
        return get_env(ENV_VAR__TESTS__GITHUB__REPO_OWNER)

    @cache_on_self
    def api_token(self):
        return get_env(ENV_VAR__GIT_HUB__ACCESS_TOKEN)

    @cache_on_self
    def environment_name(self):
        return TESTING__ENVIRONMENT__NAME

    def setup__env_vars_defined_ok(self):
        if self.api_token() and self.repo_owner() and self.repo_name():
            return True
        return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # repo secrets methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_repo_secrets(self):                                              # Create repository-level secrets for testing
        with self.github_secrets() as _:
            current_secrets = _.secrets_names()
            for secret_name in TESTING__REPO__SECRETS__NAMES:
                if secret_name not in current_secrets:
                    new_value = random_text()
                    if _.create_or_update_secret(secret_name  = secret_name ,
                                                 secret_value = new_value   ) is False:
                        raise Exception(f"in create_repo_secrets, failed to create secret: {secret_name}")
            return True

    def delete_repo_secrets(self):                                              # Delete repository-level test secrets
        with self.github_secrets() as _:
            for secret_name in TESTING__REPO__SECRETS__NAMES:
                try:
                    _.delete_secret(secret_name)
                except Exception:
                    pass                                                        # Ignore errors on cleanup
            return True

    def repo_secrets_exist(self):                                               # Check if all repo test secrets exist
        with self.github_secrets() as _:
            current_secrets = _.secrets_names()
            return all(name in current_secrets for name in TESTING__REPO__SECRETS__NAMES)

    # ═══════════════════════════════════════════════════════════════════════════════
    # environment secrets methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_env_secrets(self):                                               # Create environment-level secrets for testing
        environment_name = self.environment_name()
        if not self.ensure_environment_exists(environment_name=environment_name):                                # Create environment if needed
            return False
        with self.github_secrets() as _:
            environment_secrets = _.secrets_names(environment = environment_name)
            for secret_name in TESTING__ENV__SECRETS__NAMES:
                if secret_name not in environment_secrets:
                    new_value = random_text()
                    try:
                        if _.create_or_update_environment_secret(environment  =  environment_name,
                                                                 secret_name  = secret_name             ,
                                                                 secret_value = new_value               ) is False:
                            raise Exception(f"in create_env_secrets, failed to create secret: {secret_name}")
                    except Exception as e:
                        raise
            return True

    def delete_env_secrets(self):                                               # Delete environment-level test secrets
        with self.github_secrets() as _:
            owner = self.repo_owner()
            repo  = self.repo_name()
            for secret_name in TESTING__ENV__SECRETS__NAMES:                    # todo: refactor this to github_secrets()
                try:
                    endpoint = f"/repos/{owner}/{repo}/environments/{self.environment_name()}/secrets/{secret_name}"
                    _.api.delete(endpoint)
                except Exception:
                    pass
            return True

    def env_secrets_exist(self):                                                # Check if all env test secrets exist
        with self.github_secrets() as _:
            try:
                secrets = _.list_environment_secrets(self.environment_name())
                secret_names = [s.get('name') for s in secrets]
                return all(name in secret_names for name in TESTING__ENV__SECRETS__NAMES)
            except Exception:
                return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # organization secrets methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_org_secrets(self):                                               # Create organization-level secrets for testing
        with self.github_secrets() as _:
            org_name = self.repo_owner()
            for secret_name in TESTING__ORG__SECRETS__NAMES:
                new_value = random_text()
                try:
                    if _.create_or_update_org_secret(org_name     = org_name    ,
                                                     secret_name  = secret_name ,
                                                     secret_value = new_value   ,
                                                     visibility   = 'private'   ) is False:
                        raise Exception(f"in create_org_secrets, failed to create secret: {secret_name}")
                except Exception as e:
                    if '403' in str(e) or '404' in str(e):                       # No org admin access
                        return False
                    raise
            return True

    def delete_org_secrets(self):                                               # Delete organization-level test secrets
        with self.github_secrets() as _:
            org_name = self.repo_owner()
            for secret_name in TESTING__ORG__SECRETS__NAMES:
                try:
                    endpoint = f"/orgs/{org_name}/actions/secrets/{secret_name}"
                    _.api.delete(endpoint)
                except Exception:
                    pass
            return True

    def org_secrets_exist(self):                                                # Check if all org test secrets exist
        with self.github_secrets() as _:
            try:
                secrets = _.list_org_secrets(self.repo_owner())
                secret_names = [s.get('name') for s in secrets]
                return all(name in secret_names for name in TESTING__ORG__SECRETS__NAMES)
            except Exception:
                return False

    def has_org_admin_access(self):                                             # Check if we have org admin access
        try:
            with self.github_secrets() as _:
                _.list_org_secrets(self.repo_owner())
                return True
        except Exception:
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # environment methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def environment_exists(self, environment_name: str = None) -> bool:         # Check if a GitHub environment exists
        environment_name = environment_name or self.environment_name()
        try:
            endpoint = f"/repos/{self.repo_owner()}/{self.repo_name()}/environments/{environment_name}"
            self.github_api().get(endpoint)
            return True
        except Exception as e:
            if '404' in str(e):
                return False
            raise

    def create_environment(self, environment_name: str = None) -> bool:         # Create a GitHub environment
        environment_name = environment_name or self.environment_name()
        try:
            endpoint = f"/repos/{self.repo_owner()}/{self.repo_name()}/environments/{environment_name}"
            self.github_api().put(endpoint, {})                                 # Empty body creates basic environment
            return True
        except Exception as e:
            if '404' in str(e):                                                 # Repo doesn't exist or no access
                return False
            if '422' in str(e):                                                 # Validation error
                return False
            raise

    def ensure_environment_exists(self, environment_name: str = None) -> bool:  # Create environment if it doesn't exist
        environment_name = environment_name or self.environment_name()
        if self.environment_exists(environment_name):
            return True
        return self.create_environment(environment_name)

    def delete_environment(self, environment_name: str = None) -> bool:         # Delete a GitHub environment
        environment_name = environment_name or self.environment_name()
        try:
            endpoint = f"/repos/{self.repo_owner()}/{self.repo_name()}/environments/{environment_name}"
            self.github_api().delete(endpoint)
            return True
        except Exception as e:
            if '404' in str(e):
                return False                                                    # Already doesn't exist
            raise

    def get_environment(self, environment_name: str = None) -> dict | None:     # Get environment details
        environment_name = environment_name or self.environment_name()
        try:
            endpoint = f"/repos/{self.repo_owner()}/{self.repo_name()}/environments/{environment_name}"
            return self.github_api().get(endpoint)
        except Exception as e:
            if '404' in str(e):
                return None
            raise

    # ═══════════════════════════════════════════════════════════════════════════════
    # main methods
    # ═══════════════════════════════════════════════════════════════════════════════

    # def create(self):                                                           # Create all test data
    #     if not self.setup__env_vars_defined_ok():
    #         return False
    #     return self.create_repo_secrets()

    def create_all(self):                                                       # Create all test data including env and org secrets
        if not self.setup__env_vars_defined_ok():
            return False
        results = { 'repo_secrets': self.create_repo_secrets() ,
                    'env_secrets' : self.create_env_secrets()  ,
                    'org_secrets' : self.create_org_secrets()  }
        return results

    def cleanup_all(self):                                                      # Clean up all test data
        self.delete_repo_secrets()
        self.delete_env_secrets()
        self.delete_org_secrets()
        return True