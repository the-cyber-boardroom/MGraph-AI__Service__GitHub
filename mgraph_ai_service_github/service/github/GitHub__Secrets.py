import base64
from typing                                              import Dict, List, Any, Optional
from nacl                                                import public
from osbot_utils.decorators.methods.cache_on_self        import cache_on_self
from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from mgraph_ai_service_github.service.github.GitHub__API import GitHub__API

class GitHub__Secrets(Type_Safe):
    api_token : str
    repo_name : str
    api       : GitHub__API = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api:
            self.api = GitHub__API(api_token=self.api_token)

        # Parse repo name into owner and repo
        if '/' in self.repo_name:
            self.owner, self.repo = self.repo_name.split('/', 1)                    # todo: these should be type safe variables
        else:
            raise ValueError("repo_name must be in format 'owner/repo'")

    def _encrypt_secret(self, public_key    : str ,                                # Repository's public key
                              secret_value : str                                    # Plain text secret value
                        ) -> str:                                                   # Returns base64 encoded encrypted secret
        public_key_bytes = base64.b64decode(public_key)
        sealed_box       = public.SealedBox(public.PublicKey(public_key_bytes))
        encrypted        = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    @cache_on_self
    def get_public_key(self) -> Dict[str, str]:                                    # Get repository's public key for encryption
        endpoint = f"/repos/{self.owner}/{self.repo}/actions/secrets/public-key"
        response = self.api.get(endpoint)
        return { 'key_id' : response.get('key_id') ,
                 'key'    : response.get('key')    }

    def list_secrets(self) -> List[Dict[str, Any]]:                                # List all secrets in the repository
        endpoint = f"/repos/{self.owner}/{self.repo}/actions/secrets"
        response = self.api.get(endpoint)

        secrets = []
        for secret in response.get('secrets', []):
            secrets.append({ 'name'       : secret.get('name')       ,
                            'created_at' : secret.get('created_at') ,
                            'updated_at' : secret.get('updated_at') })

        return secrets

    def get_secret(self, secret_name : str                                         # Name of the secret
                   ) -> Optional[Dict[str, str]]:                                  # Returns secret metadata (not the value)
        try:
            endpoint = f"/repos/{self.owner}/{self.repo}/actions/secrets/{secret_name}"
            response = self.api.get(endpoint)
            return { 'name'       : response.get('name')       ,
                    'created_at' : response.get('created_at') ,
                    'updated_at' : response.get('updated_at') }
        except Exception:
            return None

    def create_or_update_secret(self, secret_name  : str ,                         # Name of the secret
                                      secret_value : str                            # Value of the secret
                                ) -> bool:                                          # Returns True if successful
        try:
            public_key_data = self.get_public_key()
            encrypted_value = self._encrypt_secret(public_key_data['key'], secret_value)

            endpoint = f"/repos/{self.owner}/{self.repo}/actions/secrets/{secret_name}"
            data     = { 'encrypted_value' : encrypted_value               ,
                        'key_id'          : public_key_data['key_id']     }

            self.api.put(endpoint, data)
            return True

        except Exception as e:
            print(f"Error creating/updating secret '{secret_name}': {e}")
            return False

    def delete_secret(self, secret_name : str                                      # Name of the secret to delete
                      ) -> bool:                                                    # Returns True if successful
        try:
            endpoint = f"/repos/{self.owner}/{self.repo}/actions/secrets/{secret_name}"
            return self.api.delete(endpoint)

        except Exception as e:
            print(f"Error deleting secret '{secret_name}': {e}")
            return False

    # todo: figure out the best way to handle the replace_all since is quite an aggressive option (by the fact that this will delete the existing secrets, without a way to recover it)
    def configure_secrets(self, secrets     : Dict[str, str]       ,               # Dictionary of secret_name: secret_value pairs
                                replace_all : bool       = False                   # Delete existing secrets not in provided dict
                          ) -> Dict[str, bool]:                                     # Returns success/failure for each operation
        results = {}

        # Get existing secrets
        existing_secrets = {s['name'] for s in self.list_secrets()}

        # Create/update provided secrets
        for secret_name, secret_value in secrets.items():
            success                        = self.create_or_update_secret(secret_name, secret_value)
            results[f"set_{secret_name}"] = success

        # Delete secrets not in the provided list if replace_all is True
        if replace_all:
            secrets_to_delete = existing_secrets - set(secrets.keys())
            for secret_name in secrets_to_delete:
                success                           = self.delete_secret(secret_name)
                results[f"delete_{secret_name}"] = success

        return results

    def secret_exists(self, secret_name : str                                      # Name of the secret
                      ) -> bool:                                                    # Returns True if the secret exists
        return self.get_secret(secret_name) is not None

    def configure_from_env_vars(self, env_mapping : Dict[str, str]                 # Maps secret_name to env_var_name
                                ) -> Dict[str, bool]:                               # Returns success/failure for each operation
        import os

        results        = {}
        secrets_to_set = {}

        for secret_name, env_var_name in env_mapping.items():
            env_value = os.getenv(env_var_name)
            if env_value:
                secrets_to_set[secret_name] = env_value
            else:
                results[f"skip_{secret_name}"] = False
                print(f"Environment variable '{env_var_name}' not found for secret '{secret_name}'")

        if secrets_to_set:
            set_results = self.configure_secrets(secrets_to_set)
            results.update(set_results)

        return results

    # Organization secrets management (requires org admin access)
    def list_org_secrets(self, org_name : str                                      # Organization name
                         ) -> List[Dict[str, Any]]:                                 # Returns list of org secrets
        endpoint = f"/orgs/{org_name}/actions/secrets"
        response = self.api.get(endpoint)

        secrets = []
        for secret in response.get('secrets', []):
            secrets.append({ 'name'       : secret.get('name')       ,
                            'created_at' : secret.get('created_at') ,
                            'updated_at' : secret.get('updated_at') ,
                            'visibility' : secret.get('visibility') ,
                            'selected_repositories_url' : secret.get('selected_repositories_url') })

        return secrets

    def create_or_update_org_secret(self, org_name     : str              ,        # Organization name
                                          secret_name  : str              ,        # Name of the secret
                                          secret_value : str              ,        # Value of the secret
                                          visibility   : str = 'selected' ,        # 'all', 'private', or 'selected'
                                          repo_ids     : List[int] = None          # List of repository IDs if visibility is 'selected'
                                    ) -> bool:                                      # Returns True if successful
        try:
            # Get org public key
            endpoint        = f"/orgs/{org_name}/actions/secrets/public-key"
            public_key_data = self.api.get(endpoint)
            encrypted_value = self._encrypt_secret(public_key_data['key'], secret_value)

            # Create/update the secret
            endpoint = f"/orgs/{org_name}/actions/secrets/{secret_name}"
            data     = { 'encrypted_value' : encrypted_value               ,
                        'key_id'          : public_key_data['key_id']     ,
                        'visibility'      : visibility                    }

            if visibility == 'selected' and repo_ids:
                data['selected_repository_ids'] = repo_ids

            self.api.put(endpoint, data)
            return True

        except Exception as e:
            print(f"Error creating/updating org secret '{secret_name}': {e}")
            return False

    # Environment secrets management
    def list_environment_secrets(self, environment : str                           # Environment name
                                ) -> List[Dict[str, Any]]:                         # Returns list of environment secrets
        endpoint = f"/repos/{self.owner}/{self.repo}/environments/{environment}/secrets"
        response = self.api.get(endpoint)

        secrets = []
        for secret in response.get('secrets', []):
            secrets.append({ 'name'       : secret.get('name')       ,
                            'created_at' : secret.get('created_at') ,
                            'updated_at' : secret.get('updated_at') })

        return secrets

    def create_or_update_environment_secret(self, environment  : str ,             # Environment name
                                                  secret_name  : str ,             # Name of the secret
                                                  secret_value : str               # Value of the secret
                                            ) -> bool:                              # Returns True if successful
        try:
            # Get environment public key
            endpoint        = f"/repos/{self.owner}/{self.repo}/environments/{environment}/secrets/public-key"
            public_key_data = self.api.get(endpoint)
            encrypted_value = self._encrypt_secret(public_key_data['key'], secret_value)

            # Create/update the secret
            endpoint = f"/repos/{self.owner}/{self.repo}/environments/{environment}/secrets/{secret_name}"
            data     = { 'encrypted_value' : encrypted_value               ,
                        'key_id'          : public_key_data['key_id']     }

            self.api.put(endpoint, data)
            return True

        except Exception as e:
            print(f"Error creating/updating environment secret '{secret_name}': {e}")
            return False