from dataclasses import dataclass
import random

from omnes_pro_uno.utils import prf as _prf


def prf(key, data, lambda_bytes):
    """Cropped to lambda bytes"""
    return _prf(key, data)[:lambda_bytes]


def ser_int(x: int):
    return x.to_bytes(8, 'little')


@dataclass
class St:
    t_ct: dict
    t_ep: dict


@dataclass
class S:
    se: bytes
    addr: bytes
    val: bytes


@dataclass
class U:
    addr: bytes
    val: bytes


class Edsse:
    def __init__(self, lambda_bytes=16, op_bytes=1, f_bytes=15, h1_seed='h1_seed', h2_seed='h2_seed', op_add=1):
        self.lambda_bytes = lambda_bytes
        self.epoch = 0
        self.op_bytes = op_bytes
        self.f_bytes = f_bytes
        def h1(x): return prf(h1_seed, x)
        self.h1 = h1
        def h2(x): return prf(h2_seed, x)
        self.h2 = h2
        """32 bytes is the output length of HMAC-SHA256"""
        assert op_bytes + f_bytes + lambda_bytes == 32
        assert len(op_add) == op_bytes
        self.OP_ADD = op_add

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
            addr = self.h1(se + bytes[1])
            val = (y + x) ^ self.h2(se + bytes[1])
        s = S(se, addr, val)
        return s, st

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
        val = (op + f + x) ^ self.h2(k_upper)
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
                buf = enb[s.addr] ^ self.h2(s.se + ser_int(ct))
                op = buf[:self.op_bytes]
                f = buf[self.op_bytes:self.op_bytes + self.f_bytes]
                x = buf[self.op_bytes + self.f_bytes:]
                if ct == 1:
                    se_prime = x
                if op == self.OP_ADD:
                    r.add(f)
                else:
                    r.remove(f)
                ct += 1
                s.addr = self.h1(s.se + ser_int(ct))
            s.se = se_prime
        return r
