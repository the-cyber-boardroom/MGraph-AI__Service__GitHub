from typing                                                                    import Dict
from fastapi                                                                   import Header
from osbot_fast_api.api.routes.Fast_API__Routes                                import Fast_API__Routes
from mgraph_ai_service_github.service.auth.Service__Auth                       import Service__Auth
from mgraph_ai_service_github.schemas.encryption.Schema__Public_Key__Response  import Schema__Public_Key__Response

TAG__ROUTES_AUTH   = 'auth'
ROUTES_PATHS__AUTH = [ f'/{TAG__ROUTES_AUTH}/public-key'       ,
                       f'/{TAG__ROUTES_AUTH}/token-create'     ,
                       f'/{TAG__ROUTES_AUTH}/token-validate'   ,
                       f'/{TAG__ROUTES_AUTH}/test'             ,
                       f'/{TAG__ROUTES_AUTH}/test-api-key'     ]

class Routes__Auth(Fast_API__Routes):
    tag          : str           = TAG__ROUTES_AUTH
    service_auth : Service__Auth

    #def public_key(self) -> Schema__Public_Key__Response:                                      # Get public key for PAT encryption
    def public_key(self):                                                                       # BUG: OSBot_Fast_API currently doesn't support mapping Type_Safe classes on GET routes return value (in practice there are no side effects at the moment since the schema validation is also not being done, and all Type_Safe objects are returned as .json() representations)
        return Schema__Public_Key__Response(public_key = self.service_auth.public_key())

    def token_create(self, github_pat : str = Header(None, alias="X-GitHub-PAT")               # Create encrypted token from PAT
                     ) -> Dict:                                                                 # Returns encrypted token
        """
        Creates an encrypted token from a GitHub PAT.
        Client sends PAT once over HTTPS, receives encrypted token for future use.
        """
        if not github_pat:
            return { "success"    : False                          ,
                    "error"      : "Missing X-GitHub-PAT header"  ,
                    "error_type" : "MISSING_HEADER"               }

        try:
            # First validate the PAT with GitHub
            github_test = self.service_auth.test_github_pat(github_pat)
            if not github_test.get("success"):
                return github_test

            # Encrypt the PAT for future use
            encrypted_pat = self.service_auth.encrypt_pat(github_pat)

            return { "success"        : True                              ,
                    "encrypted_pat"  : encrypted_pat                     ,
                    "user"           : github_test.get("user")           ,
                    "instructions"   : "Store this encrypted PAT and use it in the X-OSBot-GitHub-PAT header for future requests" }

        except Exception as e:
            return { "success"    : False                       ,
                    "error"      : f"Failed to create token: {str(e)}" ,
                    "error_type" : "ENCRYPTION_FAILED"          }

    def token_validate(self, x_osbot_github_pat : str = Header(None, alias="X-OSBot-GitHub-PAT")   # Validate encrypted token
                       ) -> Dict:                                                                    # Returns validation result
        """
        Validates an encrypted GitHub PAT token.
        Tests decryption and GitHub API access.
        """
        return self.service_auth.test(encrypted_pat=x_osbot_github_pat)

    def test(self, x_osbot_github_pat : str = Header(None, alias="X-OSBot-GitHub-PAT")        # Test encrypted PAT with GitHub API
             ) -> Dict:                                                                         # Returns test result
        """
        Tests the encrypted PAT against GitHub API.
        Returns user info and rate limit data if successful.
        """
        return self.service_auth.test(encrypted_pat=x_osbot_github_pat)

    def test_api_key(self) -> Dict:                                                            # Test service API key is valid
        """
        Tests that the service is running and accessible.
        Returns service info and auth configuration status.
        """
        return self.service_auth.test_api_key()

    def setup_routes(self):
        self.add_route_get (self.public_key     )
        self.add_route_post(self.token_create   )
        self.add_route_post(self.token_validate )
        self.add_route_get (self.test           )
        self.add_route_get (self.test_api_key   )