Pwned Password Checker
A Python-based security tool that checks if a password has been compromised in known data breaches using the Have I Been Pwned (HIBP) API.
--------
Key Features
Privacy First: Implements K-Anonymity. Only the first 5 characters of the SHA-1 hash are sent to the API.

Secure Hashing: Utilizes the hashlib library for SHA-1 generation.

Real-time Data: Fetches live data from the HIBP range API.

Local Comparison: Matches the hash suffix locally to ensure the password itself is never exposed.

🚩 Current Milestone: CLI & Security Hardening
Target Completion: Feb 16, 2026
------
Currently, the project is transitioning from a proof-of-concept script to a production-ready CLI tool. The focus for this sprint is:

Specific: Implement a robust command-line interface using argparse and secure input via getpass.

Measurable: Achieve Zero-History-Leak (passwords must not appear in shell history) and 100% success rate on edge-case character handling.

Achievable: Using Python's standard library to minimize external dependencies.

Relevant: Removing hardcoded credentials to meet real-world security standards.

How it Works
----------
The password is converted into a SHA-1 hash.

The hash is split into a 5-character prefix and the remaining suffix.

Only the prefix is sent to the HIBP API.

The API returns a list of all leaked suffixes starting with that prefix.

The tool compares the local suffix with the API results to determine the exact leak count.

Future Steps
--------
[ ] External Interface: Develop a Graphical User Interface (GUI) or a lightweight Web Frontend for non-technical users.

[ ] Password Strength Analyzer: Add a local evaluation module to check password entropy before the API lookup.

Security & Design Choices
Why SHA-1 instead of SHA-256 or SHA-3?
In most modern applications, SHA-1 is considered deprecated. However, this tool uses SHA-1 for API Compatibility.
The Have I Been Pwned database is indexed using SHA-1. By using K-Anonymity (sending only 5 characters), the known weaknesses of SHA-1 do not put the user's password at risk.
-------
Requirements
Python 3.x
-------
requests library
----
Installation
Bash
pip install requests
* `requests` library
* hashlib (preinstalled in python)
## Installation

```bash
pip install requests
