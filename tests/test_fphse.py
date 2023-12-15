import unittest
import json
from base64 import b64decode

from omnes_pro_uno.fphse import Fphse

OP_ADD = b'\x01'
F_BYTES = 15


class TestFphse(unittest.TestCase):
    def setUp(self):
        self.N = 5
        with open('tests/fixtures/fphse.json') as f:
            dbs = json.load(f)
        self.DBS = [
            {b64decode(k): b64decode(v) + b'\0' * (F_BYTES - len(b64decode(v))) for k, v in db.items()}
            for db in dbs
        ]

    def test_ok(self):
        fphse = Fphse(self.N)
        msk = fphse.rsetup()

        wk_vec = []
        e_tkn_vec = []
        st_vec = []
        enb_vec = []
        for i in range(self.N):
            wk, st, enb = fphse.wsetup()
            e_tkn, st = fphse.rebuild(i, wk, st)
            wk_vec.append(wk)
            e_tkn_vec.append(e_tkn)
            st_vec.append(st)
            enb_vec.append(enb)

        for i in range(self.N):
            dbs = self.DBS[i]
            for k, v in dbs.items():
                u_no_sse, st_vec[i] = fphse.update_token(i, wk_vec[i], st_vec[i], OP_ADD, k, v)
                enb_vec[i], e_tkn_vec[i] = fphse.update(u_no_sse, enb_vec[i], e_tkn_vec[i])

        # fphse.edsse.set_epoch(fphse.edsse.get_epoch() + 1)
        # for i in range(self.N):
        #     e_tkn_vec[i], st_vec[i] = fphse.rebuild(i, wk_vec[i], st_vec[i])

        s = [0, 1, self.N - 1]

        # for i in range(self.N):
        #     dbs = self.DBS[i]
        #     for k, v in dbs.items():
        k, v = list(self.DBS[0].items())[0]
        s_no_sse = fphse.search_token(msk, s, k)
        r, enb_vec, e_tkn_vec = fphse.search(s_no_sse, s, enb_vec, e_tkn_vec)
        if i in s:
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], v)


if __name__ == '__main__':
    unittest.main()
