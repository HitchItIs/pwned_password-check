# 🛡️ Password Leak Checker (Work in Progress 🚧)

A Python-based security tool to check if passwords have been compromised in data breaches using the 'Have I Been Pwned' API.

## 🔑 How it works (K-Anonymity)
This project implements the **K-Anonymity** principle to ensure maximum privacy:
1. Generates a **SHA-1 hash** of the input.
2. Sends only the **first 5 characters** of the hash to the API.
3. The API returns a list of all leaked hashes starting with those 5 characters.
4. The script checks locally if the full hash is in that list.
**Result:** Your actual password is never transmitted.

## 🛠️ Current State & Roadmap
This project is currently under active development. 

**What's working:**
- [x] SHA-1 Hashing of input strings.
- [x] Secure API communication via K-Anonymity.
- [x] Basic console output for leak count.

**To-do / Known Issues:**
- [x] Security: Replace hardcoded password input with secure 'getpass' or environment variables.
- [x] **Error Handling:** Currently lacks robust handling for API timeouts or connection errors.
- [ ] **File Input:** Planning to add support for checking multiple passwords from a `.txt` file.
- [ ] **UI/UX:** Improving the CLI output with `colorama` for better readability.
- [ ] **Code Refactoring:** Moving from a monolithic script to a more modular class-based structure.

## 🚀 Learning Goals
- Working with REST APIs (Requests library).
- Understanding cryptographic hashing (SHA-1).
- Practical implementation of privacy-preserving protocols.
