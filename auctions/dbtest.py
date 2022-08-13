import json
import pymongo
import sys
import os
from pathlib import Path


class AtlasStore:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient(
            f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PWD')}@cluster0.k0kxo.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client['auctions']

    def insert_report(self, report: dict) -> None:
        realm = report['realm_id']
        auctions = report['auctions']
        collection = self.db[realm]
        for item_id, auctions in auctions.items():
            collection.find_one_and_update(
                filter={'_id': item_id},
                upsert=True,
                update=[{'$addFields': {'auctions': auctions}}]
            )


"""

"""


test_document = {
    "realm_id": "510",
    "auctions": {
        "171437": {
            "1500510145": {
                "quantity": 4,
                "unit_price": 149200,
                "time_left": "LONG"
            },
            "1500517990": {
                "quantity": 10,
                "unit_price": 149200,
                "time_left": "LONG"
            },
            "1500529150": {
                "quantity": 29,
                "unit_price": 149200,
                "time_left": "LONG"
            },
            "1500571778": {
                "quantity": 2,
                "unit_price": 149200,
                "time_left": "LONG"
            },
        },
    }
}


def main():
    atlas_store = AtlasStore()
    atlas_store.insert_report(test_document)
    return 0


if __name__ == '__main__':
    sys.exit(main())
