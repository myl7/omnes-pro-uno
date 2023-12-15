import json
from random import randbytes
from base64 import b64encode

DATA_OWNER_NUM = 5
KV_PAIR_NUM = 5
KEY_LEN = 5
VAL_LEN = 5


def randstr(size):
    bs = randbytes(size)
    return b64encode(bs).decode()


dbs = [
    {randstr(KEY_LEN): randstr(VAL_LEN) for _ in range(KV_PAIR_NUM)}
    for _ in range(DATA_OWNER_NUM)
]

with open("tests/fixtures/fphse.json", "w") as f:
    json.dump(dbs, f)
