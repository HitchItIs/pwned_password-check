import asyncio
from functools import wraps
from time import monotonic
from typing import Dict, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


@rate_limited(max_concurrent=5, requests_per_second=8)
async def request_api_data(request_prefix):
    return await asyncio.to_thread(_request_api_data_sync, request_prefix)


def get_leak_count(hashes_data, target_suffix):
    lines = hashes_data.splitlines()
    for line in lines:
        if ":" not in line:
            continue
        hash_part, leak_count = line.split(':')
        if hash_part == target_suffix:
            return int(leak_count)
    return 0
