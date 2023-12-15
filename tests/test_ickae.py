import unittest

from omnes_pro_uno.ickae import Ickae


class TestIckae(unittest.TestCase):
    def setUp(self):
        self.N = 5
        self.ID = b'id'
        self.M = b'msg'

    def test_ok(self):
        ickae = Ickae(self.N)
        ickae.setup()
        msk = ickae.keygen()
        s = [0, 2, self.N - 1]
        i = s[1]
        ak = ickae.extract(msk, s, self.ID)
        c = ickae.enc(i, self.ID, self.M)
        m = ickae.dec(ak, s, i, c)
        self.assertEqual(m, self.M)


if __name__ == '__main__':
    unittest.main()
