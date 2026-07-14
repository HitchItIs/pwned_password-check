# Password Leak Checker (Work in Progress)

A Python-based security tool to check if passwords have been compromised in data breaches using the Have I Been Pwned API.

## Privacy & Security Blueprint

This project strictly prioritizes data security and implements specialized mechanisms to ensure your passwords never leave your machine or linger in memory:

1. K-Anonymity Principle: 
   * Generates a SHA-1 hash of the input.
   * Sends only the first 5 characters of the hash to the API.
   * The API returns a list of all leaked hashes starting with those 5 characters.
   * The script checks locally if the full hash is in that list.
   * Result: Your actual password is never transmitted.

2. Zero-String Memory Hitting (In Progress):
   * To prevent passwords from persisting in the RAM via immutable Python strings, this tool uses a byte-centric architecture.
   * Inputs are handled directly as mutable bytearray structures.
   * A `try...finally` cleanup path ensures the password buffer is zeroed deterministically even if hashing or API calls fail.
   * Once the hash is processed, the memory buffer is explicitly overwritten with zeroes (0x00) to mitigate memory-dump exploits.
   * CLI outputs of intermediate cryptographic pieces (like hash suffixes) are completely suppressed to avoid implicit string allocation.

## Architectural Decisions & Roadmap

This project is moving from a basic prototype to a resilient, production-grade command-line tool.

### What's working:
* Cryptographic SHA-1 Hashing of input strings.
* Secure API communication via K-Anonymity.
* basic console output for leak count.
* Asynchronous file processing for `.txt` password lists via `python pwned_checker.py /path/to/passwords.txt`.
* Security: Replace hardcoded password input with secure getpass or environment variables.
* Error Handling: Currently lacks robust handling for API timeouts or connection errors.

### Current Sprint & Refactoring (To-Do):
* Byte-Level Architecture Migration: Completely eliminate high level Python string objects for password storage and shift to native bytearray slicing.
* Resilient Error Handling (Interactive Mode): Replace hard-crashes with a continuous input loop that surfaces clear diagnostic errors (Timeouts, HTTP 503 Service unavailable) without destroying the session.
* Asynchronous File Processing: 
  * Add support for checking multiple passwords from a .txt file.
  * Implement an internal Circuit Breaker logic: if the application hits a sequence of persistent connection errors or a heavy-load response, it trips a circuit break to gracefully abort and prevent corrupted reports.
* Modular Rate-Limiting Engine:
  * Design a tunable, async throttling mechanism (Semaphore combined with a micro-delay token bucket).
  * Calibrate the delay through trial and error to process bulk lists at maximum speed just below the HIBP API's 429 (Too Many Requests) blocking threshold.

## Learning Goals
* Working with REST APIs (Requests library).
* Understanding cryptographic hashing (SHA-1).
* Practical implementation of privacy preserving protocols.
* Managing low-level memory allocation within high level language runtimes.
* Structuring scalable I/O-bound concurrency pipelines.
