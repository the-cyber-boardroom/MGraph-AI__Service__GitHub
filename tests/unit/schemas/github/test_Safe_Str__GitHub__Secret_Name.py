import re
import pytest
from unittest                                                                       import TestCase
from osbot_utils.type_safe.Type_Safe__Primitive                                     import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                 import Safe_Str
from osbot_utils.utils.Objects                                                      import base_classes
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Name import Safe_Str__GitHub__Secret_Name


class test_Safe_Str__GitHub__Secret_Name(TestCase):

    def setUp(self):
        self.error_message = re.escape("in Safe_Str__GitHub__Secret_Name, value does not match required pattern: ^[a-zA-Z_][a-zA-Z0-9_]*$")

    def test__init__(self):                                                         # Test basic initialization and type hierarchy
        with Safe_Str__GitHub__Secret_Name('MY_SECRET') as _:
            assert type(_)         is Safe_Str__GitHub__Secret_Name
            assert base_classes(_) == [Safe_Str, Type_Safe__Primitive,  str, object, object]
            assert _               == 'MY_SECRET'

    def test__init____with_underscore_prefix(self):                                 # Test names starting with underscore
        with Safe_Str__GitHub__Secret_Name('_PRIVATE_KEY') as _:
            assert _ == '_PRIVATE_KEY'

    def test__init____with_numbers(self):                                           # Test names containing numbers (not at start)
        with Safe_Str__GitHub__Secret_Name('API_KEY_V2') as _:
            assert _ == 'API_KEY_V2'

        with Safe_Str__GitHub__Secret_Name('AWS_ACCESS_KEY_123') as _:
            assert _ == 'AWS_ACCESS_KEY_123'

    def test__init____single_char(self):                                            # Test minimum length (1 char)
        with Safe_Str__GitHub__Secret_Name('A') as _:
            assert _ == 'A'

        with Safe_Str__GitHub__Secret_Name('_') as _:
            assert _ == '_'

    def test__init____max_length(self):                                             # Test maximum length (255 chars)
        max_name = 'A' * 255
        with Safe_Str__GitHub__Secret_Name(max_name) as _:
            assert _      == max_name
            assert len(_) == 255

    def test__class_attributes(self):                                               # Test class configuration
        assert Safe_Str__GitHub__Secret_Name.regex       == re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        assert Safe_Str__GitHub__Secret_Name.min_length  == 1
        assert Safe_Str__GitHub__Secret_Name.max_length  == 255
        assert Safe_Str__GitHub__Secret_Name.allow_empty == True

    # --- Invalid cases ---

    def test__init____allows_empty(self):                                          # Empty string not allowed
        assert Safe_Str__GitHub__Secret_Name('') == ''

    def test__init____rejects_number_prefix(self):                                  # Cannot start with a number
        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('123_SECRET')
        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('9API_KEY')

    def test__init____rejects_hyphen(self):                                         # Hyphens not allowed
        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('my-secret')

        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('API-KEY')

    def test__init____rejects_special_chars(self):                                  # Special characters not allowed
        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('MY.SECRET')

        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('MY@SECRET')

        with pytest.raises(ValueError, match=self.error_message):
            Safe_Str__GitHub__Secret_Name('MY SECRET')                              # Spaces not allowed

    def test__init____rejects_github_prefix(self):                                  # GITHUB_ prefix is reserved
        with pytest.raises(ValueError, match="cannot start with 'GITHUB_' prefix"):
            Safe_Str__GitHub__Secret_Name('GITHUB_TOKEN')

        with pytest.raises(ValueError, match="cannot start with 'GITHUB_' prefix"):
            Safe_Str__GitHub__Secret_Name('GITHUB_SECRET')

    def test__init____rejects_github_prefix__case_insensitive(self):                # GITHUB_ check is case-insensitive
        with pytest.raises(ValueError, match="cannot start with 'GITHUB_' prefix"):
            Safe_Str__GitHub__Secret_Name('github_token')

        with pytest.raises(ValueError, match="cannot start with 'GITHUB_' prefix"):
            Safe_Str__GitHub__Secret_Name('GitHub_Secret')

    def test__init____rejects_exceeds_max_length(self):                             # Over 255 chars not allowed
        too_long = 'A' * 256
        with pytest.raises(ValueError, match="exceeds maximum length of 255"):
            Safe_Str__GitHub__Secret_Name(too_long)

    def test__init____allows_github_in_middle(self):                                # GITHUB in middle of name is OK
        with Safe_Str__GitHub__Secret_Name('MY_GITHUB_TOKEN') as _:
            assert _ == 'MY_GITHUB_TOKEN'

        with Safe_Str__GitHub__Secret_Name('USE_GITHUB_API') as _:
            assert _ == 'USE_GITHUB_API'