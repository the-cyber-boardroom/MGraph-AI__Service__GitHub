from enum import Enum

class Enum__Encryption_Type(Enum):  # Types of content that can be encrypted/decrypted
    TEXT = "text"     # Plain text string
    JSON = "json"     # JSON object
    DATA = "data"     # Raw binary data (base64 encoded)