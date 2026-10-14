# Password Cracker & Hash Analysis Tool

Cybersecurity Internship Project — Codec Technologies  
**Project Topic 7:** Password Cracking and Hashing Algorithms

A multi-threaded password recovery and hash analysis tool written in Python 3. Built to demonstrate dictionary attacks, brute-force search space, password salting mechanics, and hash algorithm identification.

---

## Features

- **Supported Algorithms:** MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, and Windows NTLM.
- **Custom Wordlist Support:** Use the bundled SecLists 10k wordlist, provide a custom file path via `-w`, or enter the path interactively when prompted.
- **Memory-Efficient Streaming:** Reads wordlists line-by-line using Python generator (`yield`) with `latin-1` error ignoring so huge wordlists like RockYou (14 million passwords) do not crash system RAM.
- **Password Salting:** Generates cryptographically secure 16-byte random salts (`secrets.token_hex`) and demonstrates why salting breaks rainbow table attacks.
- **Salted Hash Cracking:** Supports cracking salted hashes when the salt is known.
- **Automatic Hash Detection:** Identifies candidate algorithms based on hexadecimal character count.
- **Brute-Force Mode:** Generates combinations for short passwords and numeric PINs using `itertools`.
- **CPU Speed Benchmark:** Tests and displays real-time Hashes Per Second (H/s) on your system.

---

## Project Structure

```text
password_cracker/
├── src/
│   ├── hasher.py           # Core hashing, salting, and algorithm identification
│   ├── cracker.py          # Dictionary attack and brute-force engine
│   └── main.py             # CLI interface and interactive options
├── wordlists/
│   └── 10k-most-common.txt  # Default top 10,000 password list (from SecLists)
├── sample_hashes.txt       # Precomputed test hashes for quick demonstration
└── README.md               # Documentation
```

---

## Requirements

Built entirely using Python's standard library:
- `hashlib` (OpenSSL C bindings)
- `secrets` (Cryptographically secure random generation)
- `re`, `argparse`, `time`, `itertools`, `os`, `sys`

**No third-party packages or `pip install` required.** Runs on any system with Python 3.8+.

---

## How to Run

### 1. Dictionary Attack (Auto-Detect Algorithm & Wordlist Prompt)
Run a dictionary attack against any hash. If `-w` is omitted, the tool prompts for a wordlist path or lets you press Enter to use the default:
```bash
python3 src/main.py crack -t 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
```

### 2. Dictionary Attack with Custom Wordlist (SecLists / RockYou)
Specify your own wordlist path:
```bash
python3 src/main.py crack -t 5f4dcc3b5aa765d61d8327deb882cf99 -w wordlists/10k-most-common.txt

# Or point to full rockyou:
python3 src/main.py crack -t 5f4dcc3b5aa765d61d8327deb882cf99 -w /usr/share/wordlists/rockyou.txt
```

### 3. Cracking Salted Hashes
If you know the salt used on a target hash:
```bash
python3 src/main.py crack -t a2b98d3d944bb6924d6ba2b35d0a2080801e29347c6f39bd70cd8748a0096eb2 -s cb6562c19c888a3774002965e800f5c3 -w wordlists/10k-most-common.txt
```

### 4. Hash Identification
Detect what algorithm an unknown hash was created with:
```bash
python3 src/main.py identify -t 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
# Output: 64 hex characters -> SHA-256
```

### 5. Generate Hashes (Unsalted and Salted)
```bash
# Standard hash:
python3 src/main.py hash -s "MyPassword123" -a sha256

# Salted hash (outputs both the random salt and resulting hash):
python3 src/main.py hash -s "MyPassword123" -a sha256 --salt
```

### 6. Brute-Force Attack (PINs and Short Passwords)
```bash
python3 src/main.py brute -t 81dc9bdb52d04dc20036dbd8313ed055 -a md5 -m 4
```

### 7. CPU Speed Benchmark
```bash
python3 src/main.py benchmark
```

---

## Industry Tools Analysis: John the Ripper & Hashcat

As part of analyzing industry-standard password recovery tools alongside our custom implementation, we evaluated **John the Ripper** and **Hashcat** against our target hashes:

### 1. Cracking with John the Ripper
John the Ripper leverages optimized CPU SIMD instructions (AVX2/SSE):
```bash
# Create raw hash target
echo "5f4dcc3b5aa765d61d8327deb882cf99" > raw_md5.txt

# Run dictionary attack using our SecLists wordlist
john --format=raw-md5 --wordlist=wordlists/10k-most-common.txt raw_md5.txt

# View cracked plaintext
john --show --format=raw-md5 raw_md5.txt
# Output: ?:password (1 password hash cracked)
```

### 2. Cracking with Hashcat
Hashcat utilizes GPU compute pipelines (OpenCL / CUDA) for massive parallelization:
```bash
# Dictionary attack (-a 0) against MD5 (-m 0)
hashcat -m 0 -a 0 raw_md5.txt wordlists/10k-most-common.txt

# Display cracked result
hashcat -m 0 --show raw_md5.txt
```

### 3. Tool Comparison & Architecture Analysis

| Feature / Metric | Custom Python Engine | John the Ripper | Hashcat |
|---|---|---|---|
| **Primary Target** | CPU (Python Standard Library) | CPU (AVX2 / SIMD assembly) | GPU (OpenCL / CUDA compute) |
| **Strengths** | Zero dependencies, transparent logic, cross-platform | Excellent CPU SIMD optimization, Unix crypt support | Massive parallel throughput (billions H/s on modern GPUs) |
| **Best Use Case** | Learning, scripting, CTF automation | Shadow files, rule-based CPU attacks | Bulk unsalted hash cracking at scale |
| **Salting Handling** | Prepend/append salt in code | Formats like `$dynamic_...` | Built-in salted modes (`-m 10`, `-m 20`) |

---

## Sample Output

```text
=========================================================
        Password Cracker & Hash Analysis Tool            
=========================================================

[*] Auto-detected algorithm: SHA-256
[*] Starting dictionary attack...
[*] Target Hash: 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
[*] Algorithm  : SHA-256
[*] Wordlist   : wordlists/10k-most-common.txt

[+] PASSWORD CRACKED!
    Plaintext : password
    Attempts  : 1
    Time Taken: 0.0006 seconds
    Hash Rate : 1,567 H/s
```

---

## What I Learned from this Project

1. **Hashing vs Encryption:** Hashing is a one-way mathematical function. You cannot "decrypt" a hash—you can only guess the plaintext and compare digests.
2. **Why Salts are Necessary:** Without salts, attackers use precomputed rainbow tables to look up common passwords in fractions of a second. Adding a unique random salt forces an attacker to compute a completely fresh attack for every user.
3. **Wordlist Performance in Python:** Trying to load large password lists (like `rockyou.txt` at 130MB+) using `readlines()` can freeze memory. Using a generator (`yield`) streams one line at a time with practically zero RAM overhead.
4. **Why Fast Hashes are Bad for Passwords:** MD5 and SHA-256 are designed to be fast (our benchmark reached 2+ million hashes/sec on a single CPU core). In real production systems, slow key derivation functions like **Argon2id** or **bcrypt** must be used to make offline cracking impractical.

---

## License

MIT License
