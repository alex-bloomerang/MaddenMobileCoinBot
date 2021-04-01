import json
import sys
from types import SimpleNamespace

from tinydb import TinyDB


def reformat_db(old_db, new_db):
    db = TinyDB(new_db)
    with open(old_db) as f:
        data = json.load(f)

    for key, value in data.items():
        line = json.dumps(value)
        x = json.loads(line, object_hook=lambda d: SimpleNamespace(**d))
        db.insert({"name": (key.split(" ")[1] + " " + key.split(" ")[2]).lower(),
                   "rating": int(key.split(" ")[0]),
                   "mostRecentPrice": int(x.mostRecentprice),
                   "dateOfMostRecentPrice": x.dateOfMostRecentPrice,
                   "rolling5Prices": list(map(int, x.rolling5Prices)),
                   "averagePrice": int(x.averagePrice)})


if __name__ == "__main__":
    reformat_db(sys.argv[1], sys.argv[2])
