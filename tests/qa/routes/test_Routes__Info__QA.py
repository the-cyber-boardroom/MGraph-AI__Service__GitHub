from unittest                                               import TestCase
from osbot_utils.utils.Misc                                 import list_set
from mgraph_ai_service_github.utils.testing.QA__HTTP_Client import skip_if_no_service_url, setup__qa_test_objs, QA__HTTP_Client


class test_Routes__Info__QA(TestCase):                                              # QA tests for /info/* routes against live server

    @classmethod
    def setUpClass(cls):
        skip_if_no_service_url()
        with setup__qa_test_objs() as _:
            cls.qa_test_objs = _
            cls.http_client  = _.http_client

    def test__setUpClass(self):                                                     # Verify test setup completed correctly
        with self.http_client as _:
            assert type(_)           is QA__HTTP_Client
            assert _.service_url     is not None
        with self.qa_test_objs as _:
            assert _.setup_completed is True                                       # This is on QA__Test_Objs not HTTP_Client

    def test_health(self):                                                          # GET /info/health - Basic health check
        with self.http_client as _:
            response = _.get('/info/health')

            assert response.status_code == 200
            assert response.json()      == {'status': 'ok'}

    def test_status(self):                                                          # GET /info/status - Service status with version info
        with self.http_client as _:
            response = _.get('/info/status')
            result   = response.json()

            assert response.status_code    == 200
            assert result.get('name')      == 'osbot_fast_api_serverless'
            assert result.get('status')    == 'operational'
            assert result.get('version')   is not None                              # e.g., 'v0.6.3'
            assert result.get('environment') in ['aws-lambda', 'local']

    def test_versions(self):                                                        # GET /info/versions - All component versions
        with self.http_client as _:
            response = _.get('/info/versions')
            result   = response.json()

            assert response.status_code == 200
            assert list_set(result)     == ['osbot_fast_api',
                                            'osbot_fast_api_serverless',
                                            'osbot_utils']

            assert result.get('osbot_utils'              ) is not None
            assert result.get('osbot_fast_api_serverless') is not None
            assert result.get('osbot_fast_api'           ) is not None

    def test_server(self):                                                          # GET /info/server - Server info
        with self.http_client as _:
            response = _.get('/info/server')
            result   = response.json()

            assert response.status_code == 200
            assert type(result)         is dict                                     # Server info structure varies


