import asyncio

import aiofiles

from api_client import get_leak_count, request_api_data
from security import get_hash, slicer


async def read_passwords(file_path):
    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file_handle:
            async for raw_line in file_handle:
                password = raw_line.strip()
                if not password:
                    continue
                yield password
    except OSError as err:
        print(f"File Error: Could not read '{file_path}': {err}")


async def _check_password(password_text):
    password_bytes = bytearray(password_text, encoding="utf-8")
    try:
        full_hash = get_hash(password_bytes)
        prefix, suffix = slicer(full_hash)
        api_response = await request_api_data(prefix)
        if not api_response:
            return "ERROR", 0
        count = get_leak_count(api_response, suffix)
        if count > 0:
            return "PWNED", count
        return "SAFE", 0
    finally:
        for index in range(len(password_bytes)):
            password_bytes[index] = 0x00
        del password_bytes


def _log_result(processed_count, status, leak_count):
    if status == "PWNED":
        print(f"[{processed_count}] PWNED ({leak_count} times)")
        return
    if status == "SAFE":
        print(f"[{processed_count}] SAFE")
        return
    print(f"[{processed_count}] ERROR (API request failed)")


async def process_password_file(file_path, progress_interval=100, max_in_flight=20):
    processed_count = 0
    in_flight = set()

    async for password in read_passwords(file_path):
        in_flight.add(asyncio.create_task(_check_password(password)))
        if len(in_flight) < max_in_flight:
            continue

        done, in_flight = await asyncio.wait(
            in_flight,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in done:
            status, leak_count = task.result()
            processed_count += 1
            _log_result(processed_count, status, leak_count)
            if processed_count % progress_interval == 0:
                print(f"Progress: {processed_count} passwords processed")

    while in_flight:
        done, in_flight = await asyncio.wait(
            in_flight,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in done:
            status, leak_count = task.result()
            processed_count += 1
            _log_result(processed_count, status, leak_count)
            if processed_count % progress_interval == 0:
                print(f"Progress: {processed_count} passwords processed")

    print(f"Completed: {processed_count} passwords processed")
