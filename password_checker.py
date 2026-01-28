import hashlib
import requests

def get_hash(password):
    """Generates a SHA-1 hash of the password and returns it in uppercase."""
    pw_encoded = password.encode("utf-8")
    hash_object = hashlib.sha1(pw_encoded)
    return hash_object.hexdigest().upper()

def slicer(hash_value):
    """Splits the hash into a 5-character prefix and the remaining suffix."""
    prefix = hash_value[:5]
    suffix = hash_value[5:]
    return prefix, suffix
