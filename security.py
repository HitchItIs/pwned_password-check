import hashlib


def get_hash(password):
    pw_encoded = password.encode("utf-8")
    hash_objekt = hashlib.sha1(pw_encoded)
    hex_hash = hash_objekt
    return hex_hash.hexdigest().upper()


def slicer(hash_wert):
    prefix = hash_wert[:5]
    suffix = hash_wert[5:]
    return prefix, suffix
