import base64
from typing                                                 import List, Dict, Any
from nacl.public                                            import PublicKey, SealedBox
from osbot_utils.decorators.methods.cache_on_self           import cache_on_self
from osbot_utils.type_safe.Type_Safe                        import Type_Safe
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import QA__HTTP_Client


class QA__GitHub_Secrets_Client(Type_Safe):                                         # Lightweight client for GitHub Secrets routes
    http_client : QA__HTTP_Client

    # ═══════════════════════════════════════════════════════════════════════════════
    # Setup Methods
    # ═══════════════════════════════════════════════════════════════════════════════
    @cache_on_self
    def server_public_key(self) -> str:                                             # Fetch and cache server's public key
        response = self.http_client.get('/encryption/public-key')
        result   = response.json()
        return result.get('public_key')                                             # Hex string

    @cache_on_self
    def encrypted_pat(self) -> str:                                                 # Encrypt PAT locally using server's public key
        public_key_hex   = self.server_public_key()
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key       = PublicKey(public_key_bytes)
        sealed_box       = SealedBox(public_key)
        encrypted        = sealed_box.encrypt(self.http_client.github_pat.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    @cache_on_self
    def encrypted_pat__via_token_create(self) -> str:                                                 # Get encrypted PAT for use in requests
        headers  = {'X-GitHub-PAT': self.http_client.github_pat}
        response = self.http_client.post('/auth/token-create', headers=headers)
        result   = response.json()

        if not result.get('success'):
            raise ValueError(f"Failed to create encrypted PAT: {result.get('error')}")

        return result.get('encrypted_pat')

    def _post_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        payload  = { 'encrypted_pat': self.encrypted_pat() ,
                     'request_data' : request_data         }
        response = self.http_client.post(endpoint, json=payload)
        return response.json()

    def _put_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        payload  = { 'encrypted_pat': self.encrypted_pat() ,
                     'request_data' : request_data         }
        response = self.http_client.put(endpoint, json=payload)
        return response.json()

    def _delete_request(self, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        payload  = { 'encrypted_pat': self.encrypted_pat() ,
                     'request_data' : request_data         }
        response = self.http_client.delete(endpoint, json=payload)
        return response.json()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Encryption Helper
    # ═══════════════════════════════════════════════════════════════════════════════

    def encrypt_secret_value(self, value: str) -> str:                              # Encrypt secret value locally
        public_key_hex   = self.server_public_key()
        public_key_bytes = bytes.fromhex(public_key_hex)
        public_key       = PublicKey(public_key_bytes)
        sealed_box       = SealedBox(public_key)
        encrypted        = sealed_box.encrypt(value.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')

    def encrypt_secret_value__via_server(self, value: str) -> str:                              # Encrypt a secret value for create/update
        request  = {'value': value, 'encryption_type': 'text'}
        response = self.http_client.post('/encryption/encrypt', json=request)
        result   = response.json()

        if not result.get('success'):
            raise ValueError(f"Failed to encrypt value: {result.get('error')}")

        return result.get('encrypted')

    # ═══════════════════════════════════════════════════════════════════════════════
    # Repository Secrets
    # ═══════════════════════════════════════════════════════════════════════════════

    def list_repo_secrets(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-repo/list', {'owner': owner, 'repo': repo})

    def get_repo_secret(self, owner: str, repo: str, secret_name: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-repo/get', {'owner'      : owner       ,
                                                               'repo'       : repo        ,
                                                               'secret_name': secret_name })

    def create_repo_secret(self, owner: str, repo: str, secret_name: str, secret_value: str) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        return self._post_request('/github-secrets-repo/create', {'owner'          : owner           ,
                                                                  'repo'           : repo            ,
                                                                  'secret_name'    : secret_name     ,
                                                                  'encrypted_value': encrypted_value })

    def update_repo_secret(self, owner: str, repo: str, secret_name: str, secret_value: str) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        return self._put_request('/github-secrets-repo/update', {'owner'          : owner           ,
                                                                 'repo'           : repo            ,
                                                                 'secret_name'    : secret_name     ,
                                                                 'encrypted_value': encrypted_value })

    def delete_repo_secret(self, owner: str, repo: str, secret_name: str) -> Dict[str, Any]:
        return self._delete_request('/github-secrets-repo/delete', {'owner'      : owner       ,
                                                                    'repo'       : repo        ,
                                                                    'secret_name': secret_name })

    # ═══════════════════════════════════════════════════════════════════════════════
    # Environment Secrets
    # ═══════════════════════════════════════════════════════════════════════════════

    def list_env_secrets(self, owner: str, repo: str, environment: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-env/list', {'owner'      : owner       ,
                                                               'repo'       : repo        ,
                                                               'environment': environment })

    def get_env_secret(self, owner: str, repo: str, environment: str, secret_name: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-env/get', {'owner'      : owner       ,
                                                              'repo'       : repo        ,
                                                              'environment': environment ,
                                                              'secret_name': secret_name })

    def create_env_secret(self, owner: str, repo: str, environment: str, secret_name: str, secret_value: str) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        return self._post_request('/github-secrets-env/create', {'owner'          : owner           ,
                                                                 'repo'           : repo            ,
                                                                 'environment'    : environment     ,
                                                                 'secret_name'    : secret_name     ,
                                                                 'encrypted_value': encrypted_value })

    def update_env_secret(self, owner: str, repo: str, environment: str, secret_name: str, secret_value: str) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        return self._put_request('/github-secrets-env/update', {'owner'          : owner           ,
                                                                'repo'           : repo            ,
                                                                'environment'    : environment     ,
                                                                'secret_name'    : secret_name     ,
                                                                'encrypted_value': encrypted_value })

    def delete_env_secret(self, owner: str, repo: str, environment: str, secret_name: str) -> Dict[str, Any]:
        return self._delete_request('/github-secrets-env/delete', {'owner'      : owner       ,
                                                                   'repo'       : repo        ,
                                                                   'environment': environment ,
                                                                   'secret_name': secret_name })

    # ═══════════════════════════════════════════════════════════════════════════════
    # Organization Secrets
    # ═══════════════════════════════════════════════════════════════════════════════

    def list_org_secrets(self, org: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-org/list', {'org': org})

    def get_org_secret(self, org: str, secret_name: str) -> Dict[str, Any]:
        return self._post_request('/github-secrets-org/get', {'org'        : org         ,
                                                              'secret_name': secret_name })

    def create_org_secret(self, org: str, secret_name: str, secret_value: str,
                          visibility: str = 'private', repo_ids: List[int] = None) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        request_data    = {'org'            : org             ,
                           'secret_name'    : secret_name     ,
                           'encrypted_value': encrypted_value ,
                           'visibility'     : visibility      }
        if repo_ids:
            request_data['repo_ids'] = repo_ids
        return self._post_request('/github-secrets-org/create', request_data)

    def update_org_secret(self, org: str, secret_name: str, secret_value: str,
                          visibility: str = 'private', repo_ids: List[int] = None) -> Dict[str, Any]:
        encrypted_value = self.encrypt_secret_value(secret_value)
        request_data    = {'org'            : org             ,
                           'secret_name'    : secret_name     ,
                           'encrypted_value': encrypted_value ,
                           'visibility'     : visibility      }
        if repo_ids:
            request_data['repo_ids'] = repo_ids
        return self._put_request('/github-secrets-org/update', request_data)

    def delete_org_secret(self, org: str, secret_name: str) -> Dict[str, Any]:
        return self._delete_request('/github-secrets-org/delete', {'org'        : org         ,
                                                                   'secret_name': secret_name })