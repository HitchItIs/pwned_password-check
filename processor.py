import asyncio
import logging

import aiofiles

from api_client import ApiRequestError, get_leak_count, request_api_data
from security import get_hash, slicer

logger = logging.getLogger(__name__)


async def read_passwords(file_path):
    async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file_handle:
        async for raw_line in file_handle:
            password = raw_line.strip()
            if not password:
                continue
            yield password


async def _check_password(password_text):
    password_bytes = bytearray(password_text, encoding="utf-8")
    try:
        full_hash = get_hash(password_bytes)
        prefix, suffix = slicer(full_hash)
        api_response = await request_api_data(prefix)
        count = get_leak_count(api_response, suffix)
        if count > 0:
            return "PWNED", count
        return "SAFE", 0
    except ApiRequestError:
        logger.error("Password check failed due to API error")
        return "ERROR", 0
    except Exception:
        logger.exception("Unexpected processing error for a password entry")
        return "ERROR", 0
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
    try:
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
    except OSError as err:
        logger.error("File Error: Could not read '%s': %s", file_path, err.__class__.__name__)
        raise
    finally:
        if in_flight:
            for task in in_flight:
                task.cancel()
            await asyncio.gather(*in_flight, return_exceptions=True)

    print(f"Completed: {processed_count} passwords processed")
