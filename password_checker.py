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

def request_api_data(request_prefix):
    """Requests hash suffixes from the HIBP API using the 5-char prefix."""
    url = f"https://api.pwnedpasswords.com/range/{request_prefix}"
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError(f"Error fetching data from API: {res.status_code}")
    return res.text
