import asyncio
import getpass
import sys

from api_client import get_leak_count, request_api_data
from security import get_hash, slicer


def get_password_as_bytearray():
    password_text = getpass.getpass("Password to check (or type 'exit'): ")
    try:
        return bytearray(password_text, encoding="utf-8")
    finally:
        password_text = ""
        del password_text


async def main():
    while True:
        password_bytes = get_password_as_bytearray()
        try:
            if password_bytes.lower() == b"exit":
                break
            if not password_bytes:
                continue
            full_hash = get_hash(password_bytes)
            prefix, suffix = slicer(full_hash)
            api_response = await request_api_data(prefix)
            if not api_response:
                print("Connection Error: Could not reach Pwned Passwords API.")
                continue
            count = get_leak_count(api_response, suffix)
            if count > 0:
                print(f"Danger your Password has been PWNED {count} times")
                print("Please take action ASAP!")
            else:
                print("Your password is secure.....for now!")
        finally:
            # try...finally guarantees deterministic buffer cleanup even on errors.
            for index in range(len(password_bytes)):
                password_bytes[index] = 0x00
            del password_bytes

if __name__ == "__main__":
    asyncio.run(main())
