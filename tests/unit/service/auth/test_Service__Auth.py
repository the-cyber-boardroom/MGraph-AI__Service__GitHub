import base64
from unittest                                                import TestCase
from unittest.mock                                           import patch, MagicMock

import pytest
from nacl.public                                             import PrivateKey, PublicKey, SealedBox
from osbot_utils.utils.Env                                   import set_env, get_env
from mgraph_ai_service_github.service.auth.Service__Auth     import Service__Auth


class test_Service__Auth(TestCase):
    
    @classmethod
    def setUpClass(cls):
        pytest.skip('needs private keys')
        cls.test_auth_service                                   = Service__Auth()
        cls.test_private_key_hex, cls.test_public_key_hex       = cls.test_auth_service.generate_nacl_keys()
        
        set_env('SERVICE__AUTH__PRIVATE_KEY', cls.test_private_key_hex)
        set_env('SERVICE__AUTH__PUBLIC_KEY' , cls.test_public_key_hex )
        
        cls.auth_service     = Service__Auth(private_key_hex = cls.test_private_key_hex ,
                                             public_key_hex  = cls.test_public_key_hex  )
        
        cls.test_pat             = "ghp_testtoken123456789"
        cls.encrypted_test_pat   = cls._encrypt_pat(cls.test_pat, cls.test_public_key_hex)
    
    @classmethod
    def _encrypt_pat(cls, pat         : str ,                                   # PAT to encrypt
                          public_key_hex : str                                  # Public key in hex format
                     ) -> str:                                                   # Returns base64 encoded encrypted PAT
        public_key = PublicKey(bytes.fromhex(public_key_hex))
        sealed_box = SealedBox(public_key)
        encrypted  = sealed_box.encrypt(pat.encode('utf-8'))
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    def test__init__(self):
        with self.auth_service as _:
            assert type(_)           is Service__Auth
            assert _.private_key_hex == self.test_private_key_hex
            assert _.public_key_hex  == self.test_public_key_hex
    
    def test__init__from_env(self):
        auth_service = Service__Auth()
        assert auth_service.private_key_hex == self.test_private_key_hex
        assert auth_service.public_key_hex  == self.test_public_key_hex
    
    def test_generate_nacl_keys(self):
        with self.auth_service as _:
            private_hex, public_hex = _.generate_nacl_keys()
            
            assert len(private_hex) == 64
            assert len(public_hex)  == 64
            
            bytes.fromhex(private_hex)
            bytes.fromhex(public_hex)
            
            private_key = PrivateKey(bytes.fromhex(private_hex))
            public_key  = PublicKey(bytes.fromhex(public_hex))
            
            assert bytes(private_key.public_key) == bytes(public_key)
    
    def test_public_key(self):
        with self.auth_service as _:
            public_key = _.public_key()
            assert public_key      == self.test_public_key_hex
            assert len(public_key) == 64
    
    def test_public_key__missing(self):
        auth_service = Service__Auth(private_key_hex = "test" ,
                                     public_key_hex  = ""     )
        
        with self.assertRaises(ValueError) as context:
            auth_service.public_key()
        
        assert "Public key not configured" in str(context.exception)
    
    def test_private_key(self):
        with self.auth_service as _:
            private_key = _.private_key()
            assert type(private_key) is PrivateKey
    
    def test_private_key__missing(self):
        auth_service = Service__Auth(private_key_hex = ""     ,
                                     public_key_hex  = "test" )
        
        with self.assertRaises(ValueError) as context:
            auth_service.private_key()
        
        assert "Private key not configured" in str(context.exception)
    
    def test_private_key__invalid(self):
        auth_service = Service__Auth(private_key_hex = "invalid-hex" ,
                                     public_key_hex  = "test"        )
        
        with self.assertRaises(ValueError) as context:
            auth_service.private_key()
        
        assert "Failed to load private key" in str(context.exception)
    
    def test_decrypt_pat(self):
        with self.auth_service as _:
            decrypted = _.decrypt_pat(self.encrypted_test_pat)
            assert decrypted == self.test_pat
    
    def test_decrypt_pat__invalid_base64(self):
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat("not-valid-base64!@#$")
            
            assert "Invalid base64 encoding" in str(context.exception)
    
    def test_decrypt_pat__invalid_encryption(self):
        with self.auth_service as _:
            invalid_encrypted = base64.b64encode(b"not encrypted data").decode('utf-8')
            
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat(invalid_encrypted)
            
            assert "Decryption failed" in str(context.exception)
    
    def test_decrypt_pat__missing(self):
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat("")
            
            assert "Missing encrypted PAT" in str(context.exception)
    
    def test_decrypt_pat__wrong_key(self):
        other_private_hex, other_public_hex = self.auth_service.generate_nacl_keys()
        encrypted_with_other                = self._encrypt_pat(self.test_pat, other_public_hex)
        
        with self.auth_service as _:
            with self.assertRaises(ValueError) as context:
                _.decrypt_pat(encrypted_with_other)
            
            assert "Decryption failed" in str(context.exception)
    
    @patch('mgraph_ai_service_github.service.auth.Service__Auth.GitHub__API')
    def test_test__success(self, mock_github_api_class):
        mock_github_api                     = MagicMock()
        mock_github_api_class.return_value  = mock_github_api
        
        mock_github_api.get.side_effect = [
            { "login"                     : "testuser"              ,
             "id"                        : 12345                   ,
             "name"                      : "Test User"             ,
             "email"                     : "test@example.com"      ,
             "company"                   : "Test Corp"             ,
             "created_at"                : "2020-01-01T00:00:00Z"  ,
             "public_repos"              : 42                      ,
             "total_private_repos"       : 10                      ,
             "owned_private_repos"       : 8                       ,
             "collaborators"             : 5                       ,
             "two_factor_authentication" : True                    ,
             "plan"                      : { "name"          : "pro"       ,
                                           "space"         : 976562499    ,
                                           "private_repos" : 9999         }},
            { "rate" : { "limit"     : 5000       ,
                        "remaining" : 4999       ,
                        "reset"     : 1234567890 ,
                        "used"      : 1          }}
        ]
        
        with self.auth_service as _:
            result = _.test(self.encrypted_test_pat)
            
            assert result["success"]                  is True
            assert result["error"]                    is None
            assert result["error_type"]               is None
            assert result["user"]["login"]            == "testuser"
            assert result["user"]["id"]               == 12345
            assert result["user"]["public_repos"]     == 42
            assert result["user"]["plan"]["name"]     == "pro"
            assert result["rate_limit"]["limit"]      == 5000
            assert result["rate_limit"]["remaining"]  == 4999
    
    def test_test__missing_header(self):
        with self.auth_service as _:
            result = _.test(None)
            
            assert result["success"]    is False
            assert result["error"]      == "Missing X-OSBot-GitHub-PAT header"
            assert result["error_type"] == "MISSING_HEADER"
            assert result["user"]       is None
    
    def test_test__decryption_failed(self):
        with self.auth_service as _:
            result = _.test("invalid-encrypted-data")
            
            assert result["success"]                 is False
            assert "Invalid base64 encoding"         in result["error"]
            assert result["error_type"]              == "DECRYPTION_FAILED"
    
    @patch('mgraph_ai_service_github.service.auth.Service__Auth.GitHub__API')
    def test_test__invalid_pat(self, mock_github_api_class):
        mock_github_api                    = MagicMock()
        mock_github_api_class.return_value = mock_github_api
        mock_github_api.get.side_effect    = Exception("401 Unauthorized")
        
        with self.auth_service as _:
            result = _.test(self.encrypted_test_pat)
            
            assert result["success"]         is False
            assert "Bad credentials (401)"   in result["error"]
            assert result["error_type"]      == "INVALID_PAT"
    
    @patch('mgraph_ai_service_github.service.auth.Service__Auth.GitHub__API')
    def test_test__rate_limit(self, mock_github_api_class):
        mock_github_api                    = MagicMock()
        mock_github_api_class.return_value = mock_github_api
        mock_github_api.get.side_effect    = Exception("403 API rate limit exceeded")
        
        with self.auth_service as _:
            result = _.test(self.encrypted_test_pat)
            
            assert result["success"]       is False
            assert "Rate limit exceeded"   in result["error"]
            assert result["error_type"]    == "RATE_LIMIT"
    
    def test_test_api_key(self):
        with self.auth_service as _:
            result = _.test_api_key()
            
            assert result["success"]         is True
            assert result["service"]         == "mgraph_ai_service_github"
            assert "version"                 in result
            assert result["auth_configured"] is True
            assert result["message"]         == "Service API key is valid"
    
    def test_test_api_key__no_keys_configured(self):
        auth_service = Service__Auth(private_key_hex = "" ,
                                     public_key_hex  = "" )
        result = auth_service.test_api_key()
        
        assert result["success"]         is True
        assert result["auth_configured"] is False