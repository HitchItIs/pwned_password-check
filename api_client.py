import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def get_leak_count(hashes_data, target_suffix):
    lines = hashes_data.splitlines()
    for line in lines:
        if ":" not in line:
            continue
        hash_part, leak_count = line.split(':')
        if hash_part == target_suffix:
            return int(leak_count)
    return 0
