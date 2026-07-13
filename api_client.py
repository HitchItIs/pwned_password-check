import requests


def request_api_data(request_prefix):
    try:
        url = f"https://api.pwnedpasswords.com/range/{request_prefix}"
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.text
    except requests.exceptions.RequestException:
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
