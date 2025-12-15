from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_github.schemas.encryption.Safe_Str__Encrypted_Value  import Safe_Str__Encrypted_Value
from mgraph_ai_service_github.service.auth.Service__Auth                    import Service__Auth
from mgraph_ai_service_github.service.github.GitHub__API                    import GitHub__API


class GitHub__API__From__Header(Type_Safe):                                     # Dependency for decrypting PAT and creating GitHub API instance
    service_auth: Service__Auth

    def get_api(self, encrypted_pat: Safe_Str__Encrypted_Value                  # Base64 encoded NaCl-encrypted GitHub PAT
                ) -> GitHub__API:                                               # Returns configured GitHub API instance
        decrypted_pat = self.service_auth.decrypt_pat(encrypted_pat)
        return GitHub__API(api_token=decrypted_pat)
