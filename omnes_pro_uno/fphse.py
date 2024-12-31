from dataclasses import dataclass
from nacl.exceptions import CryptoError

from omnes_pro_uno.ickae import Ickae, C, Msk
from omnes_pro_uno.edsse import Edsse, St, ser_int, U, S


@dataclass
class UNoSse:
    i: int
    c: C | None
    u: U


class Fphse:
    def __init__(self, data_owner_num):
        self.n = data_owner_num
        self.ickae = Ickae(data_owner_num)
        self.edsse = Edsse()

    def rsetup(self):
        self.ickae.setup()
        msk = self.ickae.keygen()
        return msk

    def wsetup(self):
        k, st, enb = self.edsse.setup()
        return k, st, enb

    def rebuild(self, i, k, b, st: St):
        e = self.edsse.get_epoch()
        e_tkn = []
        for w in b.keys():
            if not b.get(w, False):
                continue
            s = self.edsse.search_token(st, k, w)
            c = self.ickae.enc(i, w + ser_int(e), s.ser())
            e_tkn.append(c)
        return e_tkn, st

    def update_token(self, i, b, k, st, op, w, f):
        e = self.edsse.get_epoch()
        u, st_prime = self.edsse.update_token(st, k, op, w, f)
        if not b.get(w, False):
            s = self.edsse.search_token(st_prime, k, w)
            c = self.ickae.enc(i, w + ser_int(e), s.ser())
            b[w] = True
        else:
            c = None
        u_no_sse = UNoSse(i, c, u)
        return u_no_sse, st_prime

    def update(self, u_no_sse: UNoSse, enb, e_tkn):
        if u_no_sse.c is not None:
            e_tkn.append(u_no_sse.c)
        enb = self.edsse.update(u_no_sse.u, enb)
        return enb, e_tkn

    def search_token(self, msk: Msk, s, w):
        e = self.edsse.get_epoch()
        s = self.ickae.extract(msk, s, w + ser_int(e))
        return s

    def search(self, s_no_sse, s_perm, enb_vec, e_tkn_vec):
        r_vec = []
        for i in s_perm:
            for c in e_tkn_vec[i]:
                try:
                    s_bs = self.ickae.dec(s_no_sse, s_perm, i, c)
                except CryptoError:
                    continue
                s = S.de(s_bs)
                if s is not None:
                    r, enb_vec[i] = self.edsse.search(s, enb_vec[i])
                    r_vec.extend(r)
        return r_vec, enb_vec, e_tkn_vec
