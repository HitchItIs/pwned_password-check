import getpass
import sys

from api_client import get_leak_count, request_api_data
from security import get_hash, slicer


def main():
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
            print(f"Danger your Password has been PWNED {count} times")
            print("Please take action ASAP!")
        else:
            print("Your password is secure.....for now!")

if __name__ == "__main__":
    main()
