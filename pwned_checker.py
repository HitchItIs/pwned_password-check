import hashlib
import requests



# Generates a SHA-1 hash for the password

def get_hash(password):
    pw_encoded = password.encode("utf-8")
    hash_objekt = hashlib.sha1(pw_encoded)
    hex_hash = hash_objekt
    return hex_hash.hexdigest().upper()
# Splits hash into 5-char prefix and suffix (k-anonymity)
def slicer(hash_wert):
    prefix=hash_wert[:5]
    suffix=hash_wert[5:]
    return prefix,suffix
# Queries the Pwned Passwords API with the prefix
def request_api_data(request_prefix):
    url = f"https://api.pwnedpasswords.com/range/{request_prefix}"
    res = requests.get(url)
    if res.status_code != 200:
        raise RuntimeError ("API-Error")
    return res.text
# Checks the API response for our specific suffix
def get_leak_count(hashes_data,target_suffix):
    lines = hashes_data.splitlines()
    for line in lines: 
        hash_part, leak_count = line.split (':')
        if hash_part == target_suffix:
            return int(leak_count)
    return 0
    


if __name__ == "__main__":   
    test_password = "EnterPasswordHere"
    full_hash = get_hash(test_password)
    prefix, suffix = slicer(full_hash)
    print(f"Prefix for API: {prefix}")
    print(f"Suffix for local check: {suffix}")
    api_response = request_api_data(prefix)
    print("\n--- API Response Received ---")
    print(api_response)
    count = get_leak_count(api_response, suffix)
    if count > 0:
        print (f" Danger your Password has been PWNED {count}times")
        print ("Please take action ASAP!")
    else:
        print("no leaks have been found")

