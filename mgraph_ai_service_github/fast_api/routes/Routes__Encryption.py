from osbot_fast_api.api.Fast_API_Routes                                                 import Fast_API_Routes
from mgraph_ai_service_github.service.encryption.Service__Encryption                    import Service__Encryption
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Request            import Schema__Encryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Encryption__Response           import Schema__Encryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Request            import Schema__Decryption__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Response           import Schema__Decryption__Response
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Request  import Schema__Decryption__Validate__Request
from mgraph_ai_service_github.schemas.encryption.Schema__Decryption__Validate__Response import Schema__Decryption__Validate__Response

TAG__ROUTES_ENCRYPTION   = 'encryption'
ROUTES_PATHS__ENCRYPTION = [ f'/{TAG__ROUTES_ENCRYPTION}/public-key'        ,
                             f'/{TAG__ROUTES_ENCRYPTION}/generate-keys'     ,
                             f'/{TAG__ROUTES_ENCRYPTION}/encrypt'           ,
                             f'/{TAG__ROUTES_ENCRYPTION}/decrypt'           ,
                             f'/{TAG__ROUTES_ENCRYPTION}/validate'          ]

class Routes__Encryption(Fast_API_Routes):
    tag                : str                  = TAG__ROUTES_ENCRYPTION
    service_encryption : Service__Encryption

    #def public_key(self) -> Schema__Public_Key__Response:                                                               # Get public key for encryption
    def public_key(self):                                                                                                # BUG: OSBot_Fast_API doesn't support Type_Safe on GET return values
        return self.service_encryption.public_key()

    #def generate_keys(self) -> Schema__Key_Generation__Response:                                                        # Generate new key pair (for testing/setup)
    def generate_keys(self):
        return self.service_encryption.generate_keys()

    def encrypt(self, request : Schema__Encryption__Request) -> Schema__Encryption__Response:                           # Encrypt data with public key, Returns encrypted response
        return self.service_encryption.encrypt(request)

    def decrypt(self, request : Schema__Decryption__Request) -> Schema__Decryption__Response:                           # Decrypt data with private key, Returns decrypted response
        return self.service_encryption.decrypt(request)

    def validate(self, request : Schema__Decryption__Validate__Request) -> Schema__Decryption__Validate__Response:      # Validate encrypted data can be decrypted, Returns validation result
        return self.service_encryption.validate(request)

    def setup_routes(self):
        self.add_route_get (self.public_key    )
        self.add_route_get (self.generate_keys )
        self.add_route_post(self.encrypt       )
        self.add_route_post(self.decrypt       )
        self.add_route_post(self.validate      )