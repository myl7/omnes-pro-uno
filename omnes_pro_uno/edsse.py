from dataclasses import dataclass
import random

from omnes_pro_uno.utils import prf as _prf


def prf(key, data, lambda_bytes):
    """Cropped to lambda bytes"""
    return _prf(key, data)[:lambda_bytes]


def ser_int(x: int):
    return x.to_bytes(8, 'little')


def xor(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])


@dataclass
class St:
    t_ct: dict
    t_ep: dict


@dataclass
class S:
    se: bytes
    addr: bytes | None
    val: bytes | None

    def ser(self):
        """Simple hand-made serialization since JSON works bad on bytes"""
        if self.addr is None or self.val is None:
            return ser_int(len(self.se)) + ser_int(0) + ser_int(0) + self.se
        return ser_int(len(self.se)) + ser_int(len(self.addr)) + ser_int(len(self.val)) + self.se + self.addr + self.val

    @staticmethod
    def de(bs):
        """See `ser`"""
        se_len = int.from_bytes(bs[:8], 'little')
        addr_len = int.from_bytes(bs[8:16], 'little')
        val_len = int.from_bytes(bs[16:24], 'little')
        base = 24
        se = bs[base:base + se_len]
        base += se_len
        if addr_len == 0 or val_len == 0:
            return S(se, None, None)
        addr = bs[base:base + addr_len]
        base += addr_len
        val = bs[base:base + val_len]
        return S(se, addr, val)


@dataclass
class U:
    addr: bytes
    val: bytes


class Edsse:
    def __init__(self, lambda_bytes=16, op_bytes=1, f_bytes=15, h1_seed=b'h1_seed', h2_seed=b'h2_seed', op_add=b'\x01'):
        self.lambda_bytes = lambda_bytes
        self.epoch = 0
        self.op_bytes = op_bytes
        self.f_bytes = f_bytes
        def h1(x): return prf(h1_seed, x, lambda_bytes)
        self.h1 = h1
        def h2(x): return prf(h2_seed, x, lambda_bytes)
        self.h2 = h2
        """32 bytes is the output length of HMAC-SHA256"""
        assert op_bytes + f_bytes + lambda_bytes == 32
        assert len(op_add) == op_bytes
        self.OP_ADD = op_add

    def set_epoch(self, epoch):
        self.epoch = epoch

    def get_epoch(self):
        return self.epoch

    def setup(self):
        k = random.randbytes(self.lambda_bytes)
        t_ct = {}
        t_ep = {}
        enb = {}
        st = St(t_ct, t_ep)
        return k, st, enb

    def search_token(self, st: St, k, w):
        se = prf(k, w + ser_int(self.epoch), self.lambda_bytes)
        addr = None
        val = None
        ep = st.t_ep.get(w, None)
        if ep != self.epoch and ep is not None:
            x = prf(k, w + ser_int(ep), self.lambda_bytes)
            y = b'\0' * (self.op_bytes + self.f_bytes)
            addr = self.h1(se + bytes([1]))
            val = xor(y + x, self.h2(se + bytes([1])))
        s = S(se, addr, val)
        return s

    def update_token(self, st: St, k, op, w, f):
        if st.t_ct.get(w, None) is None or st.t_ep.get(w, None) != self.epoch:
            st.t_ct[w] = 0
        x = b'\0' * self.lambda_bytes
        st.t_ct[w] += 1
        if st.t_ct.get(w, None) == 1 and st.t_ep.get(w, None) is not None:
            x = prf(k, w + ser_int(st.t_ep[w]), self.lambda_bytes)
        st.t_ep[w] = self.epoch
        k_upper = prf(k, w + ser_int(self.epoch), self.lambda_bytes) + ser_int(st.t_ct[w])
        addr = self.h1(k_upper)
        val = xor(op + f + x, self.h2(k_upper))
        u = U(addr, val)
        return u, st

    def update(self, u: U, enb):
        enb[u.addr] = u.val
        return enb

    def search(self, s: S, enb):
        r = set()
        if s.addr is not None and s.val is not None and enb.get(s.addr, None) is None:
            enb[s.addr] = s.val
        while s.se != b'\0' * self.lambda_bytes:
            ct = 1
            s.addr = self.h1(s.se + ser_int(ct))
            se_prime = b'\0' * self.lambda_bytes
            while enb.get(s.addr, None) is not None:
                buf = xor(enb[s.addr], self.h2(s.se + ser_int(ct)))
                op = buf[:self.op_bytes]
                f = buf[self.op_bytes:self.op_bytes + self.f_bytes]
                x = buf[self.op_bytes + self.f_bytes:]
                if ct == 1:
                    se_prime = x
                if op == self.OP_ADD:
                    r.add(f)
                else:
                    if f in r:
                        r.remove(f)
                ct += 1
                s.addr = self.h1(s.se + ser_int(ct))
            s.se = se_prime
        return r, enb
