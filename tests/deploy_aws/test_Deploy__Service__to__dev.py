from unittest                                    import TestCase
from tests.deploy_aws.test_Deploy__Service__base import test_Deploy__Service__base

class test_Deploy__Service__to__dev(test_Deploy__Service__base, TestCase):
    stage = 'dev'

    # def test_x__create_keys(self):
    #     key_management = NaCl__Key_Management()
    #     pprint(key_management.generate_nacl_keys().json())

    # def test_2__check_dependencies(self):
    #     upload_results = self.deploy_fast_api.upload_lambda_dependencies_to_s3()
    #     #pprint(upload_results.get('pynacl==1.5.0').get('local_result').json())
    #
    def test_3__install_again(self):
        self.test_3__create()
    #
    # def test_4__invoke__return_logs(self):
    #     payload = {}
    #     response = self.deploy_fast_api.lambda_function().invoke(payload)
    #     pprint(response)