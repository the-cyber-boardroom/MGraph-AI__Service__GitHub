from osbot_utils.type_safe.Type_Safe                          import Type_Safe
from osbot_utils.utils.Env                                    import get_env
from mgraph_ai_service_github.config                          import DEPLOY__GITHUB__REPO__OWNER, DEPLOY__GITHUB__REPO__NAME, ENV_VAR__GIT_HUB__ACCESS_TOKEN
from mgraph_ai_service_github.service.github.GitHub__Secrets  import GitHub__Secrets


class Setup__GitHub__Repo(Type_Safe):
    github_secrets: GitHub__Secrets = None
    repo_name     : str             = f"{DEPLOY__GITHUB__REPO__OWNER}/{DEPLOY__GITHUB__REPO__NAME}"

    def __init__(self):
        super().__init__()
        self.github_secrets = GitHub__Secrets(repo_name=self.repo_name)


    def repo_secrets(self):
        secrets = {}
        for secret in self.github_secrets.list_secrets():
            secrets[secret.get('name')] = secret
        return secrets

    def gh_access_token__name(self):
        return ENV_VAR__GIT_HUB__ACCESS_TOKEN

    def gh_access_token__exists(self)-> bool:
        return self.repo_secrets().get(self.gh_access_token__name()) is not None

    def gh_access_token__update(self):
        secret_name  = self.gh_access_token__name()
        secret_value = get_env(secret_name)
        if secret_value:
            return self.github_secrets.create_or_update_secret(secret_name=secret_name, secret_value=secret_value)
        return False

    def update__env_vars(self, env_vars):
        for env_var in env_vars:
            secret_name  = env_var
            secret_value = get_env(env_var)
            if not secret_value:
                return False
            if not self.github_secrets.create_or_update_secret(secret_name=secret_name, secret_value=secret_value):
                return False
        return True

    def update__env_vars__aws_deploy(self):
        aws_vars = ['AWS_ACCOUNT_ID'        ,
                    'AWS_DEFAULT_REGION'    ,
                    'AWS_ACCESS_KEY_ID'     ,
                    'AWS_SECRET_ACCESS_KEY' ]
        return self.update__env_vars(aws_vars)

    def update__env_vars__fast_api(self):
        fast_api_vars = ['FAST_API__AUTH__API_KEY__NAME',
                         'FAST_API__AUTH__API_KEY__VALUE']
        return self.update__env_vars(fast_api_vars)

