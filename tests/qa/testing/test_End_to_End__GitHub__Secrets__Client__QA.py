from unittest                                                         import TestCase
from osbot_utils.utils.Env                                            import get_env, load_dotenv
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client           import skip_if_no_service_url, skip_if_no_github_pat, setup__qa_test_objs
from mgraph_ai_service_github.utils.testing.QA__GitHub_Secrets_Client import QA__GitHub_Secrets_Client



class test_End_to_End__GitHub__Secrets__Client__QA(TestCase):                       # Tests for QA__GitHub_Secrets_Client itself

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        skip_if_no_github_pat()
        load_dotenv()

        with setup__qa_test_objs() as _:
            cls.http_client = _.http_client
            cls.github_pat  = str(_.http_client.github_pat)

    def test__client_initialization(self):                                          # Verify client initializes correctly
        client = QA__GitHub_Secrets_Client(http_client = self.http_client ,
                                           github_pat  = self.github_pat  )

        assert type(client)           is QA__GitHub_Secrets_Client
        assert client.http_client     is self.http_client
        assert client.github_pat      == self.github_pat

        print("\n  ✓ Client initialized correctly")

    def test__encrypted_pat_caching(self):                                          # Verify encrypted_pat is cached
        client = QA__GitHub_Secrets_Client(http_client = self.http_client ,
                                           github_pat  = self.github_pat  )

        # First call - should make API request
        pat_1 = client.encrypted_pat()
        assert pat_1 is not None

        # Second call - should return cached value
        pat_2 = client.encrypted_pat()
        assert pat_2 is not None

        assert pat_1 == pat_2                                                       # Same cached value

        print("\n  ✓ Encrypted PAT is cached correctly")

    def test__encrypt_secret_value(self):                                           # Verify secret value encryption works
        client = QA__GitHub_Secrets_Client(http_client = self.http_client ,
                                           github_pat  = self.github_pat  )

        test_value = 'test_secret_value_123'
        encrypted  = client.encrypt_secret_value(test_value)

        assert encrypted is not None
        assert encrypted != test_value                                              # Should be different from plaintext
        assert len(encrypted) > len(test_value)                                     # Encrypted should be longer

        print(f"\n  ✓ Secret value encrypted: {len(test_value)} chars → {len(encrypted)} chars")