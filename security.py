import hashlib


def get_hash(password):
    if isinstance(password, str):
        password = password.encode("utf-8")
    return hashlib.sha1(password).hexdigest().upper()


def slicer(hash_wert):
    prefix = hash_wert[:5]
    suffix = hash_wert[5:]
    return prefix, suffix
