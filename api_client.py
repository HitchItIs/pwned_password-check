import asyncio
from functools import wraps
from time import monotonic
from typing import Dict, Tuple

import requests


RETRY_DELAYS = [0.5, 1, 2, 5, 20, 60]
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


class _RateLimitState:
    def __init__(self, max_concurrent, requests_per_second):
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be >= 1")
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0")
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.requests_per_second = requests_per_second
        self.bucket_capacity = max(1.0, float(requests_per_second))
        self.tokens = self.bucket_capacity
        self.last_refill = monotonic()
        self._token_lock = asyncio.Lock()

    async def acquire_token(self):
        while True:
            async with self._token_lock:
                now = monotonic()
                elapsed = now - self.last_refill
                self.tokens = min(
                    self.bucket_capacity,
                    self.tokens + (elapsed * self.requests_per_second),
                )
                self.last_refill = now

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return

                wait_time = (1.0 - self.tokens) / self.requests_per_second
            await asyncio.sleep(wait_time)


_RATE_LIMIT_STATES: Dict[Tuple[int, float], _RateLimitState] = {}


def _get_rate_limit_state(max_concurrent, requests_per_second):
    key = (max_concurrent, float(requests_per_second))
    state = _RATE_LIMIT_STATES.get(key)
    if state is None:
        state = _RateLimitState(max_concurrent, float(requests_per_second))
        _RATE_LIMIT_STATES[key] = state
    return state


def rate_limited(max_concurrent, requests_per_second):
    state = _get_rate_limit_state(max_concurrent, requests_per_second)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await state.acquire_token()
            async with state.semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def _request_api_data_sync(request_prefix):
    url = f"https://api.pwnedpasswords.com/range/{request_prefix}"
    try:
        res = requests.get(url, timeout=5)
        return res.status_code, res.text
    except requests.exceptions.RequestException as err:
        print(f"API request failed: {err}")
        return None, ""


@rate_limited(max_concurrent=5, requests_per_second=8)
async def request_api_data(request_prefix):
    retry_count = 0

    while True:
        status_code, response_text = await asyncio.to_thread(
            _request_api_data_sync,
            request_prefix,
        )

        if status_code == 200:
            return response_text

        if status_code in RETRY_STATUS_CODES:
            delay = RETRY_DELAYS[min(retry_count, len(RETRY_DELAYS) - 1)]
            print(
                f"Warning: retry attempt {retry_count + 1}, "
                f"HTTP {status_code}, waiting {delay} seconds.",
            )
            retry_count += 1
            await asyncio.sleep(delay)
            continue

        if status_code is not None:
            print(f"API request failed with HTTP {status_code}")
        return ""


def get_leak_count(hashes_data, target_suffix):
    lines = hashes_data.splitlines()
    for line in lines:
        if ":" not in line:
            continue
        hash_part, leak_count = line.split(':')
        if hash_part == target_suffix:
            return int(leak_count)
    return 0
