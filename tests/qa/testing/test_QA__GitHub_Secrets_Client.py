from unittest                                                           import TestCase
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.utils.Objects                                          import base_classes
from mgraph_ai_service_github.utils.testing.QA__GitHub_Secrets_Client   import QA__GitHub_Secrets_Client


class test_QA__GitHub_Secrets_Client(TestCase):                                     # Unit tests for QA__GitHub_Secrets_Client structure

    def test__init__(self):                                                         # Test class structure
        assert QA__GitHub_Secrets_Client.__bases__ == (Type_Safe,)
        assert base_classes(QA__GitHub_Secrets_Client) == [Type_Safe, object]

    def test__class_attributes(self):                                               # Test class has expected attributes
        annotations = QA__GitHub_Secrets_Client.__annotations__

        assert 'http_client' in annotations
        assert 'github_pat'  in annotations

    def test__methods_exist(self):                                                  # Test expected methods exist
        methods = dir(QA__GitHub_Secrets_Client)

        # Setup methods
        assert 'encrypted_pat'        in methods
        assert 'encrypt_secret_value' in methods

        # Repo secrets methods
        assert 'list_repo_secrets'   in methods
        assert 'get_repo_secret'     in methods
        assert 'create_repo_secret'  in methods
        assert 'update_repo_secret'  in methods
        assert 'delete_repo_secret'  in methods

        # Env secrets methods
        assert 'list_env_secrets'    in methods
        assert 'get_env_secret'      in methods
        assert 'create_env_secret'   in methods
        assert 'update_env_secret'   in methods
        assert 'delete_env_secret'   in methods

        # Org secrets methods
        assert 'list_org_secrets'    in methods
        assert 'get_org_secret'      in methods
        assert 'create_org_secret'   in methods
        assert 'update_org_secret'   in methods
        assert 'delete_org_secret'   in methods