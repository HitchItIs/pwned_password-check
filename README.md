# Pwned Password Checker

A Python-based security tool that checks if a password has been compromised in known data breaches using the Have I Been Pwned (HIBP) API.

## Key Features

* **Privacy First:** Implements **K-Anonymity**. Only the first 5 characters of the SHA-1 hash are sent to the API.
* **Secure Hashing:** Utilizes the `hashlib` library for SHA-1 generation.
* **Real-time Data:** Fetches live data from the HIBP range API.
* **Local Comparison:** Matches the hash suffix locally to ensure the password itself is never exposed.

## How it Works

1.  The password is converted into a **SHA-1 hash**.
2.  The hash is split into a **5-character prefix** and the remaining **suffix**.
3.  Only the **prefix** is sent to the HIBP API.
4.  The API returns a list of all leaked suffixes starting with that prefix.
5.  The tool compares the local suffix with the API results to determine the exact leak count.



## Security & Design Choices

### Why SHA-1 instead of SHA-256 or SHA-3?
In most modern applications, SHA-1 is considered deprecated due to collision vulnerabilities. However, this tool uses SHA-1 for **API Compatibility**. 

The *Have I Been Pwned* database is historically indexed using SHA-1. To use their range API and benefit from their massive dataset, we must provide the SHA-1 prefix. Since we use **K-Anonymity** (only sending the first 5 characters), the known weaknesses of SHA-1 do not put the user's password at risk in this specific implementation.

## Requirements

* Python 3.x
* `requests` library
* hashlib (preinstalled in python)
## Installation

```bash
pip install requests
