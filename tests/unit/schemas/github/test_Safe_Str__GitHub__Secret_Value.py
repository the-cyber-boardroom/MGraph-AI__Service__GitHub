import pytest
from unittest                                                                        import TestCase
from osbot_utils.type_safe.Type_Safe__Primitive                                      import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                  import Safe_Str
from osbot_utils.utils.Objects                                                       import base_classes
from mgraph_ai_service_github.schemas.github.safe_str.Safe_Str__GitHub__Secret_Value import Safe_Str__GitHub__Secret_Value


class test_Safe_Str__GitHub__Secret_Value(TestCase):

    def test__init__(self):                                                         # Test basic initialization and type hierarchy
        with Safe_Str__GitHub__Secret_Value('my-secret-value-123') as _:
            assert type(_)         is Safe_Str__GitHub__Secret_Value
            assert base_classes(_) == [Safe_Str, Type_Safe__Primitive, str, object, object]
            assert _               == 'my-secret-value-123'

    def test__init____with_empty(self):                                             # Empty allowed for serialization
        with Safe_Str__GitHub__Secret_Value('') as _:
            assert _ == ''

    def test__init____with_special_chars(self):                                     # Test that printable special chars are allowed
        with Safe_Str__GitHub__Secret_Value('p@$$w0rd!#%^&*()') as _:
            assert _ == 'p@$$w0rd!#%^&*()'

    def test__init____with_json(self):                                              # Test JSON content (common for service accounts)
        json_value = '{"type":"service_account","project_id":"my-project"}'
        with Safe_Str__GitHub__Secret_Value(json_value) as _:
            assert _ == json_value

    def test__init____with_multiline(self):                                         # Test multiline content (SSH keys, certs)
        multiline = "-----BEGIN RSA PRIVATE KEY-----\nMIIE...base64...\n-----END RSA PRIVATE KEY-----"
        with Safe_Str__GitHub__Secret_Value(multiline) as _:
            assert _ == multiline

    def test__init____with_tabs_and_newlines(self):                                 # Tabs, LF, CR are preserved (not stripped)
        value_with_whitespace = "line1\tvalue\nline2\rline3"
        with Safe_Str__GitHub__Secret_Value(value_with_whitespace) as _:
            assert _ == value_with_whitespace
            assert '\t' in _                                                        # Tab preserved
            assert '\n' in _                                                        # LF preserved
            assert '\r' in _                                                        # CR preserved

    def test__init____with_unicode(self):                                           # Test unicode content
        unicode_value = '密码：测试123'
        with Safe_Str__GitHub__Secret_Value(unicode_value) as _:
            assert _ == unicode_value

    def test__init____with_whitespace(self):                                        # Test whitespace handling
        with Safe_Str__GitHub__Secret_Value('  spaced  value  ') as _:
            assert _ == '  spaced  value  '                                         # Whitespace preserved (no trim)

    def test__init____single_char(self):                                            # Test minimum length (1 char)
        with Safe_Str__GitHub__Secret_Value('x') as _:
            assert _ == 'x'

    def test__class_attributes(self):                                               # Test class configuration
        assert Safe_Str__GitHub__Secret_Value.max_length  == 48 * 1024              # 49,152 bytes
        assert Safe_Str__GitHub__Secret_Value.min_length  == 1
        assert Safe_Str__GitHub__Secret_Value.allow_empty == True                   # Changed for serialization

    def test__init____near_max_length(self):                                        # Test near maximum size (48 KB)
        large_value = 'A' * (48 * 1024)                                             # Exactly 48 KB
        with Safe_Str__GitHub__Secret_Value(large_value) as _:
            assert len(_) == 48 * 1024

    # --- Control character sanitization (REPLACE mode) ---

    def test__init____strips_null(self):                                            # NULL char stripped
        with Safe_Str__GitHub__Secret_Value('secret\x00value') as _:
            assert _ == 'secret_value'

    def test__init____strips_control_chars(self):                                   # Control chars \x01-\x08 stripped
        with Safe_Str__GitHub__Secret_Value('abc\x01\x02\x03\x07\x08def') as _:
            assert _ == 'abc_____def'

    def test__init____strips_vt_and_ff(self):                                       # VT (\x0B) and FF (\x0C) stripped
        with Safe_Str__GitHub__Secret_Value('line1\x0Bline2\x0Cline3') as _:
            assert _ == 'line1_line2_line3'

    def test__init____strips_so_to_us(self):                                        # \x0E-\x1F stripped
        with Safe_Str__GitHub__Secret_Value('test\x0E\x0F\x1E\x1Fend') as _:
            assert _ == 'test____end'

    def test__init____strips_del(self):                                             # DEL char (\x7F) stripped
        with Safe_Str__GitHub__Secret_Value('secret\x7Fvalue') as _:
            assert _ == 'secret_value'

    def test__init____preserves_printable_after_strip(self):                        # Complex case: strip control, keep rest
        messy_input  = 'API_KEY\x00=\x01abc123\x7F!'
        clean_output = 'API_KEY_=_abc123_!'
        with Safe_Str__GitHub__Secret_Value(messy_input) as _:
            assert _ == clean_output

    # --- Invalid cases ---

    def test__init____rejects_exceeds_max_length(self):                             # Over 48 KB not allowed
        too_large = 'A' * (48 * 1024 + 1)
        with pytest.raises(ValueError, match="exceeds maximum length"):
            Safe_Str__GitHub__Secret_Value(too_large)

    def test__init____byte_size_consideration(self):                                # Test byte size with multibyte chars
        # Each emoji is 4 bytes in UTF-8
        # 48 KB = 49,152 bytes = 12,288 four-byte chars
        emoji_value = '🔐' * 12288                                                  # Exactly 48 KB in bytes
        with Safe_Str__GitHub__Secret_Value(emoji_value) as _:
            assert len(_)                  == 12288                                 # Character count
            assert len(_.encode('utf-8'))  == 49152                                 # Byte count = 48 KB