import time
import os
import itertools
import string
from hasher import make_hash


def stream_wordlist(wordlist_path):
    # check if wordlist file exists first
    if not os.path.exists(wordlist_path):
        raise FileNotFoundError(f"Wordlist file not found: {wordlist_path}")

    # using yield to stream line-by-line so big wordlists like rockyou don't eat all RAM.
    # latin-1 + errors='ignore' prevents crashes on weird symbols in leaked databases.
    with open(wordlist_path, "r", encoding="latin-1", errors="ignore") as f:
        for line in f:
            word = line.strip("\r\n")
            if word:
                yield word


def crack_dictionary(target_hash, wordlist_path, algo="sha256", salt=None):
    target = target_hash.strip().lower()
    attempts = 0
    start_time = time.time()

    print(f"[*] Starting dictionary attack...")
    print(f"[*] Target Hash: {target}")
    print(f"[*] Algorithm  : {algo.upper()}")
    print(f"[*] Wordlist   : {wordlist_path}")
    if salt:
        print(f"[*] Salt       : {salt}")

    for word in stream_wordlist(wordlist_path):
        attempts += 1

        # if salted, prepend salt to word
        test_text = f"{salt}{word}" if salt else word
        candidate_hash = make_hash(test_text, algo)

        if candidate_hash == target:
            elapsed = time.time() - start_time
            rate = int(attempts / elapsed) if elapsed > 0 else attempts
            return {
                "success": True,
                "password": word,
                "attempts": attempts,
                "time": round(elapsed, 4),
                "speed": rate,
            }

        # print status every 50,000 attempts so we know it hasn't frozen
        if attempts % 50000 == 0:
            elapsed = time.time() - start_time
            print(f"[+] Checked {attempts:,} words... ({int(attempts/elapsed):,} H/s)")

    elapsed = time.time() - start_time
    return {
        "success": False,
        "password": None,
        "attempts": attempts,
        "time": round(elapsed, 4),
        "speed": int(attempts / elapsed) if elapsed > 0 else attempts,
    }


def crack_bruteforce(target_hash, max_length=4, charset=None, algo="sha256"):
    # default to lowercase letters + digits (a-z, 0-9)
    if charset is None:
        charset = string.ascii_lowercase + string.digits

    target = target_hash.strip().lower()
    attempts = 0
    start_time = time.time()

    print(f"[*] Starting brute force (up to {max_length} characters)...")
    print(f"[*] Target Hash: {target}")
    print(f"[*] Character set: {len(charset)} chars")

    # try lengths from 1 up to max_length
    for length in range(1, max_length + 1):
        for combo in itertools.product(charset, repeat=length):
            attempts += 1
            candidate = "".join(combo)
            candidate_hash = make_hash(candidate, algo)

            if candidate_hash == target:
                elapsed = time.time() - start_time
                return {
                    "success": True,
                    "password": candidate,
                    "attempts": attempts,
                    "time": round(elapsed, 4),
                }

    elapsed = time.time() - start_time
    return {
        "success": False,
        "password": None,
        "attempts": attempts,
        "time": round(elapsed, 4),
    }
