#!/usr/bin/env python3
import argparse
import os
import sys
import time
from hasher import make_hash, make_salted_hash, detect_hash_type, ALGOS
from cracker import crack_dictionary, crack_bruteforce

# colors for output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# default wordlist path
DEFAULT_WORDLIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "wordlists",
    "10k-most-common.txt"
)


def banner():
    print(f"{CYAN}{BOLD}")
    print("=========================================================")
    print("        Password Cracker & Hash Analysis Tool            ")
    print("=========================================================")
    print(f"{RESET}")


def resolve_wordlist(provided_path):
    # if user passed a path via -w flag, check if it exists
    if provided_path:
        if os.path.exists(provided_path):
            return provided_path
        print(f"{YELLOW}[!] Wordlist path not found: {provided_path}{RESET}")

    # otherwise ask interactively
    print(f"{CYAN}[?] Wordlist Selection:{RESET}")
    print(f"    Press [Enter] to use default (SecLists 10k: {DEFAULT_WORDLIST})")
    user_input = input("    Or enter your wordlist path: ").strip()

    if user_input:
        expanded = os.path.expanduser(user_input)
        if os.path.exists(expanded):
            return expanded
        print(f"{RED}[-] Path does not exist. Falling back to default wordlist.{RESET}")

    if os.path.exists(DEFAULT_WORDLIST):
        return DEFAULT_WORDLIST

    print(f"{RED}[-] Error: Default wordlist not found. Please provide a valid wordlist path.{RESET}")
    sys.exit(1)


def cmd_crack(args):
    target = args.target.strip()
    algo = args.algo.lower() if args.algo else None

    # if user didn't specify algorithm, guess it from the hash length
    if not algo:
        detected = detect_hash_type(target)
        if detected and "Not a valid" not in detected[0] and "Unknown" not in detected[0]:
            algo = detected[0].lower()
            if "/" in algo:
                algo = algo.split("/")[0].lower()
            print(f"{YELLOW}[*] Auto-detected algorithm: {algo.upper()}{RESET}")
        else:
            algo = "sha256"
            print(f"{YELLOW}[*] Defaulting algorithm to: SHA-256{RESET}")

    wordlist = resolve_wordlist(args.wordlist)
    result = crack_dictionary(target, wordlist, algo=algo, salt=args.salt)

    print()
    if result["success"]:
        print(f"{GREEN}{BOLD}[+] PASSWORD CRACKED!{RESET}")
        print(f"    Plaintext : {BOLD}{result['password']}{RESET}")
        print(f"    Attempts  : {result['attempts']:,}")
        print(f"    Time Taken: {result['time']} seconds")
        print(f"    Hash Rate : {result['speed']:,} H/s")
    else:
        print(f"{RED}[-] Password not found in wordlist.{RESET}")
        print(f"    Attempts  : {result['attempts']:,}")
        print(f"    Time Taken: {result['time']} seconds")


def cmd_brute(args):
    target = args.target.strip()
    algo = args.algo.lower() if args.algo else "sha256"
    max_len = args.max_len

    result = crack_bruteforce(target, max_length=max_len, algo=algo)

    print()
    if result["success"]:
        print(f"{GREEN}{BOLD}[+] PASSWORD CRACKED!{RESET}")
        print(f"    Plaintext : {BOLD}{result['password']}{RESET}")
        print(f"    Attempts  : {result['attempts']:,}")
        print(f"    Time Taken: {result['time']} seconds")
    else:
        print(f"{RED}[-] Not found in keyspace (length <= {max_len}).{RESET}")
        print(f"    Attempts  : {result['attempts']:,}")


def cmd_hash(args):
    text = args.string
    algo = args.algo.lower()

    if args.salt:
        digest, salt = make_salted_hash(text, algo=algo)
        print(f"{GREEN}[+] Salted Hash Created:{RESET}")
        print(f"    Algorithm: {algo.upper()}")
        print(f"    Salt     : {salt}")
        print(f"    Hash     : {digest}")
    else:
        digest = make_hash(text, algo=algo)
        print(f"{GREEN}[+] Hash Created:{RESET}")
        print(f"    Algorithm: {algo.upper()}")
        print(f"    Hash     : {digest}")


def cmd_identify(args):
    target = args.target.strip()
    candidates = detect_hash_type(target)
    print(f"{CYAN}[*] Hash Analysis:{RESET}")
    print(f"    Hash Length   : {len(target)} characters ({len(target) * 4} bits)")
    print(f"    Probable Type : {', '.join(candidates)}")


def cmd_benchmark():
    print(f"{CYAN}[*] Running speed test (100,000 hashes each)...{RESET}\n")
    test_word = "internship_test_2026"
    iterations = 100000

    for name in ["md5", "sha1", "sha256", "sha512"]:
        start = time.time()
        for _ in range(iterations):
            make_hash(test_word, algo=name)
        elapsed = time.time() - start
        rate = int(iterations / elapsed)
        print(f"    {name.upper():<8} : {rate:,} Hashes/sec ({round(elapsed, 3)}s)")
    print(f"\n{GREEN}[+] Benchmark done.{RESET}")


def main():
    banner()

    parser = argparse.ArgumentParser(
        description="Password Cracker & Hash Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # crack command
    crack_parser = subparsers.add_parser("crack", help="Dictionary attack against hash")
    crack_parser.add_argument("-t", "--target", required=True, help="Target hash to crack")
    crack_parser.add_argument("-w", "--wordlist", help="Path to custom wordlist")
    crack_parser.add_argument("-a", "--algo", help="Algorithm (md5, sha1, sha256, sha512, ntlm)")
    crack_parser.add_argument("-s", "--salt", help="Known salt string")

    # brute command
    brute_parser = subparsers.add_parser("brute", help="Brute-force short passwords/PINs")
    brute_parser.add_argument("-t", "--target", required=True, help="Target hash to crack")
    brute_parser.add_argument("-m", "--max-len", type=int, default=4, help="Max length (default: 4)")
    brute_parser.add_argument("-a", "--algo", default="sha256", help="Algorithm (default: sha256)")

    # hash command
    hash_parser = subparsers.add_parser("hash", help="Generate hash from text")
    hash_parser.add_argument("-s", "--string", required=True, help="Text to hash")
    hash_parser.add_argument("-a", "--algo", default="sha256", help="Algorithm (default: sha256)")
    hash_parser.add_argument("--salt", action="store_true", help="Add random salt")

    # identify command
    ident_parser = subparsers.add_parser("identify", help="Guess hash type by length")
    ident_parser.add_argument("-t", "--target", required=True, help="Hash to identify")

    # benchmark command
    subparsers.add_parser("benchmark", help="Measure hashing speed on this machine")

    args = parser.parse_args()

    if args.command == "crack":
        cmd_crack(args)
    elif args.command == "brute":
        cmd_brute(args)
    elif args.command == "hash":
        cmd_hash(args)
    elif args.command == "identify":
        cmd_identify(args)
    elif args.command == "benchmark":
        cmd_benchmark()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
