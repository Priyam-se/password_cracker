import hashlib
import secrets
import re

# hash algorithm mapping
ALGOS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}

# hash length to type mapping based on hex length
# 32 chars = 128 bit (md5/ntlm), 64 chars = 256 bit (sha256), etc.
HASH_LENGTHS = {
    32: ["MD5", "NTLM"],
    40: ["SHA-1"],
    56: ["SHA-224"],
    64: ["SHA-256"],
    96: ["SHA-384"],
    128: ["SHA-512"],
}


def make_hash(text, algo="sha256"):
    # clean algo string so sha-256 or SHA256 both work
    algo = algo.lower().replace("-", "")

    # windows ntlm hashes use md4 over utf-16le encoded string
    if algo == "ntlm":
        return hashlib.new("md4", text.encode("utf-16le")).hexdigest()

    if algo not in ALGOS:
        raise ValueError(f"Algorithm {algo} not supported. Use one of: {list(ALGOS.keys()) + ['ntlm']}")

    # compute hash and return hex string
    h = ALGOS[algo]()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def make_salted_hash(text, salt=None, algo="sha256"):
    # generate random 16 bytes salt if not passed
    if not salt:
        salt = secrets.token_hex(16)

    # prepend salt to word before hashing (salt + password)
    # this makes precomputed rainbow tables useless
    combined = f"{salt}{text}"
    return make_hash(combined, algo), salt


def detect_hash_type(hash_str):
    hash_str = hash_str.strip().lower()

    # check if string is actually valid hex (0-9, a-f)
    if not re.fullmatch(r"^[0-9a-f]+$", hash_str):
        return ["Not a valid hex hash"]

    length = len(hash_str)
    return HASH_LENGTHS.get(length, [f"Unknown ({length} chars)"])
