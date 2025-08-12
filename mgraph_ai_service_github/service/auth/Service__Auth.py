import base64
import nacl.exceptions
from typing                                              import Dict, Optional, Tuple
from nacl.public                                         import PrivateKey, PublicKey, SealedBox
import nacl.utils
from osbot_utils.decorators.methods.cache_on_self        import cache_on_self
from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from osbot_utils.utils.Env                               import get_env
from mgraph_ai_service_github.service.github.GitHub__API import GitHub__API


class Service__Auth(Type_Safe):
    private_key_hex : str = None
    public_key_hex  : str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.private_key_hex:
            self.private_key_hex = get_env('SERVICE__AUTH__PRIVATE_KEY', '')
        if not self.public_key_hex:
            self.public_key_hex = get_env('SERVICE__AUTH__PUBLIC_KEY', '')

    @cache_on_self
    def private_key(self) -> PrivateKey:                                        # Load and cache the private key object
        if not self.private_key_hex:
            raise ValueError("Private key not configured - SERVICE__AUTH__PRIVATE_KEY environment variable is missing")

        try:
            private_bytes = bytes.fromhex(self.private_key_hex)
            return PrivateKey(private_bytes)
        except Exception as e:
            raise ValueError(f"Failed to load private key: {str(e)}")

    @cache_on_self
    def public_key_object(self) -> PublicKey:                                   # Get PublicKey object for internal use
        if not self.public_key_hex:
            raise ValueError("Public key not configured - SERVICE__AUTH__PUBLIC_KEY environment variable is missing")

        try:
            public_bytes = bytes.fromhex(self.public_key_hex)
            return PublicKey(public_bytes)
        except Exception as e:
            raise ValueError(f"Failed to load public key: {str(e)}")

    def public_key(self) -> str:                                                # Return the public key hex string for clients
        if not self.public_key_hex:
            raise ValueError("Public key not configured - SERVICE__AUTH__PUBLIC_KEY environment variable is missing")
        return self.public_key_hex

    def decrypt_pat(self, encrypted_pat : str                                   # Base64 encoded encrypted PAT
                    ) -> str:                                                    # Returns the decrypted PAT
        if not encrypted_pat:
            raise ValueError("Missing encrypted PAT")

        try:
            encrypted_bytes = base64.b64decode(encrypted_pat)
            sealed_box      = SealedBox(self.private_key())
            decrypted_pat   = sealed_box.decrypt(encrypted_bytes)

            return decrypted_pat.decode('utf-8')

        except base64.binascii.Error as e:
            raise ValueError(f"Invalid base64 encoding: {str(e)}")
        except nacl.exceptions.CryptoError as e:
            raise ValueError("Decryption failed: Invalid encrypted format or wrong key")
        except Exception as e:
            raise ValueError(f"Failed to decrypt PAT: {str(e)}")

    def test(self, encrypted_pat : str = None                                   # Test the encrypted PAT against GitHub
             ) -> Dict:                                                          # Returns user info or error details

        response = { "success"    : False ,
                    "error"      : None  ,
                    "error_type" : None  ,
                    "user"       : None  ,
                    "rate_limit" : None  }

        if not encrypted_pat:
            response["error"]      = "Missing X-OSBot-GitHub-PAT header"
            response["error_type"] = "MISSING_HEADER"
            return response

        try:
            decrypted_pat = self.decrypt_pat(encrypted_pat)
        except Exception as e:
            response["error"]      = str(e)
            response["error_type"] = "DECRYPTION_FAILED"
            return response

        try:
            github_api      = GitHub__API(api_token=decrypted_pat)
            user_data       = github_api.get('/user')
            rate_limit_data = github_api.get('/rate_limit')

            response["success"] = True
            response["user"]    = { "login"                     : user_data.get("login")                      ,
                                   "id"                        : user_data.get("id")                          ,
                                   "name"                      : user_data.get("name")                        ,
                                   "email"                     : user_data.get("email")                       ,
                                   "company"                   : user_data.get("company")                    ,
                                   "created_at"                : user_data.get("created_at")                 ,
                                   "public_repos"              : user_data.get("public_repos")               ,
                                   "total_private_repos"       : user_data.get("total_private_repos")        ,
                                   "owned_private_repos"       : user_data.get("owned_private_repos")        ,
                                   "collaborators"             : user_data.get("collaborators")              ,
                                   "two_factor_authentication" : user_data.get("two_factor_authentication")  ,
                                   "plan"                      : { "name"          : user_data.get("plan", {}).get("name")         ,
                                                                  "space"         : user_data.get("plan", {}).get("space")        ,
                                                                  "private_repos" : user_data.get("plan", {}).get("private_repos")} if user_data.get("plan") else None}

            response["rate_limit"] = { "limit"     : rate_limit_data.get("rate", {}).get("limit")     ,
                                      "remaining" : rate_limit_data.get("rate", {}).get("remaining") ,
                                      "reset"     : rate_limit_data.get("rate", {}).get("reset")     ,
                                      "used"      : rate_limit_data.get("rate", {}).get("used")      }

        except Exception as e:
            error_message = str(e)

            if "401" in error_message:
                response["error"]      = "GitHub API error: Bad credentials (401)"
                response["error_type"] = "INVALID_PAT"
            elif "403" in error_message and "rate limit" in error_message.lower():
                response["error"]      = "GitHub API error: Rate limit exceeded"
                response["error_type"] = "RATE_LIMIT"
            elif "403" in error_message:
                response["error"]      = "GitHub API error: Forbidden - PAT may lack required scopes"
                response["error_type"] = "INVALID_PAT"
            elif "404" in error_message:
                response["error"]      = "GitHub API error: Resource not found (404)"
                response["error_type"] = "GITHUB_ERROR"
            else:
                response["error"]      = f"GitHub API error: {error_message}"
                response["error_type"] = "GITHUB_ERROR"

        return response

    def test_api_key(self) -> Dict:                                             # Test that the service is running and accessible
        from mgraph_ai_service_github.utils.Version import version__mgraph_ai_service_github
        from mgraph_ai_service_github.config        import SERVICE_NAME

        return { "success"         : True                                                              ,
                "service"         : SERVICE_NAME                                                      ,
                "version"         : version__mgraph_ai_service_github                                 ,
                "auth_configured" : bool(self.private_key_hex and self.public_key_hex)                ,
                "message"         : "Service API key is valid"                                        }


    def encrypt_pat(self, github_pat : str                                      # Plain text GitHub PAT to encrypt
                     ) -> str:                                                  # Returns base64 encoded encrypted PAT
        """
        Encrypts a GitHub PAT for storage and reuse.
        Uses the service's public key to create a SealedBox encryption.
        """
        if not github_pat:
            raise ValueError("GitHub PAT cannot be empty")

        try:
            pat_bytes       = github_pat.encode('utf-8')
            public_key      = self.public_key_object()
            sealed_box      = SealedBox(public_key)
            encrypted_bytes = sealed_box.encrypt(pat_bytes)

            return base64.b64encode(encrypted_bytes).decode('utf-8')

        except Exception as e:
            raise ValueError(f"Failed to encrypt PAT: {str(e)}")


    def test_github_pat(self, github_pat : str                                  # Plain text GitHub PAT to test
                        ) -> Dict:                                               # Returns test result with user info
        """
        Tests a plain text GitHub PAT directly against GitHub API.
        Used during token creation to validate PAT before encryption.
        """
        response = { "success"    : False ,
                    "error"      : None  ,
                    "error_type" : None  ,
                    "user"       : None  ,
                    "rate_limit" : None  }

        if not github_pat:
            response["error"]      = "GitHub PAT cannot be empty"
            response["error_type"] = "INVALID_INPUT"
            return response

        try:
            github_api      = GitHub__API(api_token=github_pat)
            user_data       = github_api.get('/user')
            rate_limit_data = github_api.get('/rate_limit')

            response["success"] = True
            response["user"]    = { "login"                     : user_data.get("login")                      ,
                                   "id"                        : user_data.get("id")                          ,
                                   "name"                      : user_data.get("name")                        ,
                                   "email"                     : user_data.get("email")                       ,
                                   "company"                   : user_data.get("company")                    ,
                                   "created_at"                : user_data.get("created_at")                 ,
                                   "public_repos"              : user_data.get("public_repos")               ,
                                   "total_private_repos"       : user_data.get("total_private_repos")        ,
                                   "owned_private_repos"       : user_data.get("owned_private_repos")        ,
                                   "collaborators"             : user_data.get("collaborators")              ,
                                   "two_factor_authentication" : user_data.get("two_factor_authentication")  ,
                                   "plan"                      : { "name"          : user_data.get("plan", {}).get("name")         ,
                                                                  "space"         : user_data.get("plan", {}).get("space")        ,
                                                                  "private_repos" : user_data.get("plan", {}).get("private_repos")} if user_data.get("plan") else None}

            response["rate_limit"] = { "limit"     : rate_limit_data.get("rate", {}).get("limit")     ,
                                      "remaining" : rate_limit_data.get("rate", {}).get("remaining") ,
                                      "reset"     : rate_limit_data.get("rate", {}).get("reset")     ,
                                      "used"      : rate_limit_data.get("rate", {}).get("used")      }

        except Exception as e:
            error_message = str(e)

            if "401" in error_message:
                response["error"]      = "GitHub API error: Bad credentials (401)"
                response["error_type"] = "INVALID_PAT"
            elif "403" in error_message and "rate limit" in error_message.lower():
                response["error"]      = "GitHub API error: Rate limit exceeded"
                response["error_type"] = "RATE_LIMIT"
            elif "403" in error_message:
                response["error"]      = "GitHub API error: Forbidden - PAT may lack required scopes"
                response["error_type"] = "INVALID_PAT"
            elif "404" in error_message:
                response["error"]      = "GitHub API error: Resource not found (404)"
                response["error_type"] = "GITHUB_ERROR"
            else:
                response["error"]      = f"GitHub API error: {error_message}"
                response["error_type"] = "GITHUB_ERROR"

        return response