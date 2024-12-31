from hashlib import sha256
import hmac

from nacl.utils import randombytes_deterministic


def prf(key, data):
    """HMAC-SHA256"""
    return hmac.new(key, data, sha256).digest()


def enc(key, data):
    return xor(data, G(key, len(data)))


def dec(key, data):
    return xor(data, G(key, len(data)))


def G(seed: bytes, out_len: int) -> bytes:
    return randombytes_deterministic(out_len, sha256(seed).digest())


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])
