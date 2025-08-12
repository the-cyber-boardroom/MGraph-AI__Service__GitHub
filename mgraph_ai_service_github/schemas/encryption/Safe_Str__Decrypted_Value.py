from osbot_utils.helpers.safe_str.Safe_Str                          import Safe_Str
from osbot_utils.type_safe.Type_Safe__Primitive                     import Type_Safe__Primitive
from mgraph_ai_service_github.schemas.encryption.Const__Encryption  import TYPE_SAFE_STR__DECRYPTED_DATA__MAX_LENGTH


class Safe_Str__Decrypted_Value(Type_Safe__Primitive,str):
    """
    Safe string class for base64-encoded decrypted data.
    """
    max_length      = TYPE_SAFE_STR__DECRYPTED_DATA__MAX_LENGTH
    allow_empty     = False
    trim_whitespace = True