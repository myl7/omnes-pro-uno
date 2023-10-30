from hashlib import sha256
import hmac

from nacl.secret import SecretBox


def prf(key, data):
    """HMAC-SHA256"""
    return hmac.new(key, data, sha256).digest()


def enc(key, data):
    """
    XSalsa20-Poly1305.
    Returns `(nonce, ciphertext)`.
    """
    msg = SecretBox(key).encrypt(data)
    return (msg.nonce, msg.ciphertext)


def dec(key, nonce, data):
    """XSalsa20-Poly1305"""
    return SecretBox(key).decrypt(data, nonce)
