from functools import reduce
from dataclasses import dataclass

from charm.toolbox.pairinggroup import PairingGroup, G1, G2, pair, extract_key

from omnes_pro_uno.utils import prf, enc as enc_f, dec as dec_f


def prod(iter): return reduce(lambda a, b: a * b, iter)
def e(a, b): return pair(a, b)


@dataclass
class Msk:
    gamma: int
    delta: int


@dataclass
class Pk:
    gamma_g2: int
    delta_g2: int


@dataclass
class Ak:
    k: int
    b: int


@dataclass
class C:
    c1: int
    c2: int
    c30: (bytes, bytes)
    c31: (bytes, bytes)


class Ickae:
    def __init__(self, data_owner_num):
        self.n = data_owner_num
        self.group = PairingGroup('MNT224')
        self.g1 = self.group.random(G1)
        self.g2 = self.group.random(G2)
        self.gt = e(self.g1, self.g2)
        assert self.g1.initPP(), "failed to init pre-computation table"
        assert self.g2.initPP(), "failed to init pre-computation table"
        assert self.gt.initPP(), "failed to init pre-computation table"

    def setup(self):
        self.alpha = self.group.random()
        self.alpha_g1s = [self.g1 ** self.alpha ** i for i in range(1, 2 * self.n + 1)]
        self.alpha_g2s = [self.g2 ** self.alpha ** i for i in range(1, self.n + 1)]
        self.alpha_gt = self.gt ** self.alpha ** (self.n + 1)

    def keygen(self):
        gamma = self.group.random()
        delta = self.group.random()
        msk = Msk(gamma, delta)
        gamma_g2 = self.g2 ** gamma
        delta_g2 = self.g2 ** delta
        pk = Pk(gamma_g2, delta_g2)
        self.pk = pk
        return msk

    def ext(self, msk: Msk, s, id: bytes):
        b = prf(id, b'b')[0] & 0b1
        hb = self.group.hash(id + bytes([b]), G1)
        k = prod([self.alpha_g1s[self.n - 1 - j] for j in s]) ** msk.gamma * hb ** msk.delta
        ak = Ak(k, b)
        return ak

    def enc(self, i, id: bytes, m: bytes):
        r = self.group.random()
        c1 = self.g2 ** r
        c2 = (self.pk.gamma_g2 * self.alpha_g2s[i]) ** r
        h0 = self.group.hash(id + bytes([0]), G1)
        h1 = self.group.hash(id + bytes([1]), G1)
        c30 = enc_f(extract_key(self.alpha_gt ** r / e(h0, self.pk.delta_g2) ** r), m)
        c31 = enc_f(extract_key(self.alpha_gt ** r / e(h1, self.pk.delta_g2) ** r), m)
        c = C(c1, c2, c30, c31)
        return c

    def dec(self, ak: Ak, s, i, c: C):
        u = prod([e(self.alpha_g1s[self.n - 1 - j], c.c2) for j in s]) \
            / e((ak.k * prod([self.alpha_g1s[self.n + i - j] for j in s if j != i])), c.c1)
        c3b = c.c30 if ak.b == 0 else c.c31
        return dec_f(extract_key(u), c3b[0], c3b[1])
