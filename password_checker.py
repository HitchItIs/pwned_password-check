import hashlib
import requests

def get_hash(password):
    """Generates a SHA-1 hash of the password and returns it in uppercase."""
    pw_encoded = password.encode("utf-8")
    hash_object = hashlib.sha1(pw_encoded)
    return hash_object.hexdigest().upper()
