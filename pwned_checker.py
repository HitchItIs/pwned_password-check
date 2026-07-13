import hashlib
import requests
import getpass
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=frozenset(["GET"]),
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    try:
        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            res = session.get(url, timeout=5)
            res.raise_for_status()
            return res.text
    except requests.exceptions.RequestException as err:
        print(f"API request failed after retries: {err}")
        return ""

# Checks the API response for our specific suffix

def get_leak_count(hashes_data,target_suffix):
    lines = hashes_data.splitlines()
    for line in lines: 
        if ":" not in line : continue
        hash_part, leak_count = line.split (':')
        if hash_part == target_suffix:
            return int(leak_count)
    return 0

#Main

if __name__ == "__main__":
    while True:   
     test_password = getpass.getpass("Password to check (or type 'exit'): ")
     if test_password.lower() == "exit":
         break
     if not test_password:
         continue
     full_hash = get_hash(test_password)
     prefix, suffix = slicer(full_hash)
     api_response = request_api_data(prefix)
     if not api_response:
        print("Connection Error: Could not reach Pwned Passwords API.")
        continue
     count = get_leak_count(api_response, suffix)
     if count > 0:
        print (f"Danger your Password has been PWNED {count} times")
        print ("Please take action ASAP!")
     else: 
        print("Your password is secure.....for now!")