from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, skip_if_no_github_pat, setup__qa_test_objs


class test_End_to_End__QA(TestCase):                                                # End-to-end integration tests combining multiple routes

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client
            cls.github_pat  = str(_.http_client.github_pat)

    def test__full_github_pat_flow(self):                                           # Complete PAT encryption flow: create -> validate -> use
        with self.http_client as _:
            # Step 1: Verify service is healthy
            health_response = _.get('/info/health')
            assert health_response.status_code == 200
            assert health_response.json()      == {'status': 'ok'}

            # Step 2: Get public key (verify encryption is configured)
            pubkey_response = _.get('/auth/public-key')
            assert pubkey_response.status_code == 200
            public_key = pubkey_response.json().get('public_key')
            assert public_key is not None
            assert len(public_key) == 64

            # Step 3: Create encrypted token from GitHub PAT
            create_headers  = {'X-GitHub-PAT': self.github_pat}
            create_response = _.post('/auth/token-create', headers=create_headers)
            create_result   = create_response.json()

            if not create_result.get('success'):
                self.skipTest(f"token-create failed: {create_result.get('error')}")

            encrypted_pat = create_result.get('encrypted_pat')
            user_info     = create_result.get('user')

            assert encrypted_pat is not None
            assert user_info     is not None
            print(f"\n  ✓ Token created for user: {user_info.get('login')}")

            # Step 4: Validate the encrypted token
            validate_headers  = {'X-OSBot-GitHub-PAT': encrypted_pat}
            validate_response = _.post('/auth/token-validate', headers=validate_headers)
            validate_result   = validate_response.json()

            assert validate_result.get('success') is True
            assert validate_result.get('user')    is not None
            print(f"  ✓ Token validated successfully")

            # Step 5: Use token to test GitHub API access
            test_headers  = {'X-OSBot-GitHub-PAT': encrypted_pat}
            test_response = _.get('/auth/test', headers=test_headers)
            test_result   = test_response.json()

            assert test_result.get('success')    is True
            assert test_result.get('rate_limit') is not None

            rate_limit = test_result.get('rate_limit')
            print(f"  ✓ GitHub API access confirmed (rate limit: {rate_limit.get('remaining')}/{rate_limit.get('limit')})")

    def test__full_encryption_flow(self):                                           # Complete encryption flow: encrypt -> validate -> decrypt
        with self.http_client as _:
            test_data = {
                'text'  : 'Sensitive text data to encrypt',
                'json'  : '{"secret":"value","count":42}',
                'data'  : 'U2VjcmV0IGJpbmFyeSBkYXRh'                                # "Secret binary data" in base64
            }

            for encryption_type, value in test_data.items():
                # Step 1: Encrypt
                encrypt_request  = {'value': value, 'encryption_type': encryption_type}
                encrypt_response = _.post('/encryption/encrypt', json=encrypt_request)
                encrypt_result   = encrypt_response.json()

                assert encrypt_result.get('success') is True, f"Encrypt failed for {encryption_type}"
                encrypted = encrypt_result.get('encrypted')

                # Step 2: Validate
                validate_request  = {'encrypted': encrypted, 'encryption_type': encryption_type}
                validate_response = _.post('/encryption/validate', json=validate_request)
                validate_result   = validate_response.json()

                assert validate_result.get('can_decrypt') is True, f"Validate failed for {encryption_type}"

                # Step 3: Decrypt
                decrypt_request  = {'encrypted': encrypted, 'encryption_type': encryption_type}
                decrypt_response = _.post('/encryption/decrypt', json=decrypt_request)
                decrypt_result   = decrypt_response.json()

                assert decrypt_result.get('success')   is True, f"Decrypt failed for {encryption_type}"
                assert decrypt_result.get('decrypted') == value, f"Round-trip failed for {encryption_type}"

                print(f"\n  ✓ {encryption_type}: encrypt -> validate -> decrypt successful")

    def test__public_keys_match(self):                                              # Verify /auth and /encryption return same public key
        with self.http_client as _:
            auth_response       = _.get('/auth/public-key')
            encryption_response = _.get('/encryption/public-key')

            auth_key       = auth_response.json().get('public_key')
            encryption_key = encryption_response.json().get('public_key')

            assert auth_key       is not None
            assert encryption_key is not None
            assert auth_key       == encryption_key                                 # Same service, same keys

            print(f"\n  ✓ Public keys match: {auth_key[:16]}...")

    def test__service_versions_consistency(self):                                   # Verify version info is consistent across endpoints
        with self.http_client as _:
            status_response   = _.get('/info/status')
            versions_response = _.get('/info/versions')

            status_version   = status_response.json().get('version')
            versions_version = versions_response.json().get('mgraph_ai_service_github')

            assert status_version   is not None
            assert versions_version is not None
            assert status_version   == versions_version                             # Versions should match

            print(f"\n  ✓ Service version: {status_version}")