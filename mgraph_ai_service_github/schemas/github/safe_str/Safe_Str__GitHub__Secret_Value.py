import re

from osbot_utils.type_safe.primitives.core.Safe_Str import Safe_Str

TYPE_SAFE_STR__HTML__SECRET_VALUE = re.compile(r'[\x00\x01-\x08\x0B\x0C\x0E-\x1F\x7F]')

class Safe_Str__GitHub__Secret_Value(Safe_Str):
    """Type-safe string for GitHub Secret Values.

    GitHub secret value constraints:
    - Max 48 KB (49,152 bytes)
    - Any characters allowed
    - Cannot be empty
    """

    max_length  = 48 * 1024  # 49,152 bytes
    min_length  = 1
    allow_empty = True
    regex       = TYPE_SAFE_STR__HTML__SECRET_VALUE