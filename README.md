# Pwned Password Checker

A Python-based security tool that checks if a password has been compromised in known data breaches using the **Have I Been Pwned (HIBP) API**.

## Key Features
- **Privacy First:** Implements **K-Anonymity**. Only the first 5 characters of the SHA-1 hash are sent to the API.
- **Secure Hashing:** Utilizes the `hashlib` library for SHA-1 generation.
- **Real-time Data:** Fetches live data from the HIBP range API.

## How it Works
1. The password is converted into a **SHA-1 hash**.
2. The hash is split into a **5-character prefix** and the remaining **suffix**.
3. Only the **prefix** is sent to the HIBP API.
4. The API returns a list of all leaked suffixes starting with that prefix.
5. (Upcoming) The tool compares the local suffix with the API results to determine if the password is safe.

## Requirements
- Python 3.x
- `requests` library

## Installation
```bash
pip install requests
