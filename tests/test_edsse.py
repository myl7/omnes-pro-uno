import unittest

from omnes_pro_uno.edsse import Edsse


class TestEdsse(unittest.TestCase):
    def setUp(self):
        pass  # TODO

    def test_ok(self):
        edsse = Edsse()
        k, st, enb = edsse.setup()
        pass  # TODO


if __name__ == '__main__':
    # unittest.main()
    pass
