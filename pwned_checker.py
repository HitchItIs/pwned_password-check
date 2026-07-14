import asyncio
import getpass
import logging
import sys
 
from api_client import ApiRequestError, get_leak_count, request_api_data
from processor import process_password_file
from security import get_hash, slicer
 
logger = logging.getLogger(__name__)


def get_password_as_bytearray():
    password_text = getpass.getpass("Password to check (or type 'exit'): ")
    try:
        return bytearray(password_text, encoding="utf-8")
    finally:
        password_text = ""
        del password_text


async def interactive_main():
    while True:
        password_bytes = get_password_as_bytearray()
        try:
            if password_bytes.lower() == b"exit":
                break
            if not password_bytes:
                continue
            full_hash = get_hash(password_bytes)
            prefix, suffix = slicer(full_hash)
            try:
                api_response = await request_api_data(prefix)
            except ApiRequestError:
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


async def main():
    try:
        if len(sys.argv) > 1:
            await process_password_file(sys.argv[1])
            return
        await interactive_main()
    except OSError:
        print("Error: Failed to read input file.")
    except Exception:
        logger.exception("Unexpected fatal error")
        print("Error: Unexpected failure. Please try again.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
