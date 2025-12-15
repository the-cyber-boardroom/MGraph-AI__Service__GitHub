from unittest                                    import TestCase
from tests.deploy_aws.test_Deploy__Service__base import test_Deploy__Service__base

class test_Deploy__Service__to__dev(test_Deploy__Service__base, TestCase):
    stage = 'dev'

    # def test_x__create_keys(self):
    #     key_management = NaCl__Key_Management()
    #     pprint(key_management.generate_nacl_keys().json())

    # def test_2__check_dependencies(self):
    #     from osbot_utils.utils.Dev import pprint
    #     upload_results = self.deploy_fast_api.upload_lambda_dependencies_to_s3()
    #     package_to_see = 'osbot-fast-api-serverless==v1.32.0'
    #     local_result = upload_results.get(package_to_see).get('local_result')
    #     local_result.print_obj()
    # #
    # def test_3__install_again(self):
    #     self.test_3__create()
    # #
    # def test_4__invoke__return_logs(self):
    #     self.test_3__create()
    #     from osbot_utils.utils.Dev import pprint
    #     payload = {}
    #     response = self.deploy_fast_api.lambda_function().invoke(payload)
    #     pprint(response)