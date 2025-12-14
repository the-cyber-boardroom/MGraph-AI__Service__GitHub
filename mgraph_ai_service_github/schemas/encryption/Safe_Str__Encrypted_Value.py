import base64
from osbot_utils.type_safe.Type_Safe__Primitive                     import Type_Safe__Primitive
from mgraph_ai_service_github.schemas.encryption.Const__Encryption  import TYPE_SAFE_STR__ENCRYPTED_DATA__MAX_LENGTH


class Safe_Str__Encrypted_Value(Type_Safe__Primitive, str):
    """
    Safe string class for base64-encoded encrypted data.

    This validates that a string is valid base64 and within reasonable size limits
    for encrypted data that will be transmitted via API.

    Examples:
    - "dGhpcyBpcyBhIHRlc3Q=" (base64)
    - Encrypted NaCl SealedBox output (base64 encoded)

    The actual encrypted data will be longer than the original due to:
    - NaCl overhead (48 bytes for SealedBox)
    - Base64 encoding (increases size by ~33%)
    """
    max_length      = TYPE_SAFE_STR__ENCRYPTED_DATA__MAX_LENGTH
    allow_empty     = False
    trim_whitespace = True

    def __new__(cls, value):
        try:
            decoded = base64.b64decode(value, validate=True)                            # Check if it's valid base64 by trying to decode

            if len(decoded) < 48:                                                       # Ensure it has minimum length (at least NaCl overhead) , NaCl SealedBox adds 48 bytes overhead
                raise ValueError(f"Encrypted data too short to be valid NaCl encryption: {len(decoded)} bytes")

        except Exception as e:
            raise ValueError(f"Invalid base64 encoded encrypted data: {str(e)}")

        return super().__new__(cls, value)