import re
from typing                                                                 import Optional
from osbot_utils.type_safe.primitives.core.Safe_Str                         import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode import Enum__Safe_Str__Regex_Mode

TYPE_SAFE__STR__REGEX__SECRET_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

class Safe_Str__GitHub__Secret_Name(Safe_Str):
    """Type-safe string for GitHub Secret Names.

    GitHub secret name constraints:
    - Only alphanumeric characters [a-zA-Z0-9] and underscores [_]
    - Cannot start with a number
    - Cannot start with GITHUB_ prefix (reserved)
    - Max 255 characters
    """

    regex             = TYPE_SAFE__STR__REGEX__SECRET_NAME
    min_length        = 1
    max_length        = 255
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    strict_validation = True

    def __new__(cls, value: Optional[str] = None) -> 'Safe_Str__GitHub__Secret_Name':

        value = super().__new__(cls, value)         # parent handles regex + length checks

        if value.upper().startswith('GITHUB_'):
            raise ValueError(f"in {cls.__name__}, secret names cannot start with 'GITHUB_' prefix (reserved): {value}" ) from None

        return value