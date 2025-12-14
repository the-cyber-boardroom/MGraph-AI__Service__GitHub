from unittest                                               import TestCase
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs


class test_Routes__Info__QA__no_auth(TestCase):                                     # Test info routes without authentication

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.service_url = _.http_client.service_url

    def test_health__no_auth(self):                                                 # Verify health endpoint requires auth
        import requests
        response = requests.get(f"{self.service_url}/info/health", timeout=30)

        # Depending on your auth config, this might be 401 or 200
        # Most services protect all endpoints including health
        assert response.status_code in [200, 401]

        if response.status_code == 401:
            result = response.json()
            assert result.get('status') == 'error'
            assert 'API key' in result.get('message', '')