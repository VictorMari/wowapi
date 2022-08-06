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
        collection = self.db[realm]
        for item_id, auctions in report['auctions'].items():
            item_document = collection.find_one({'_id': item_id})
            print("doc", item_document)

            if not item_document:
                collection.insert_one({'_id': item_id, 'auctions': auctions})

            else:
                all_auctions = item_document['auctions'].extend(auctions)
                unique_auctions = list(set(all_auctions, key=lambda x: x['id']))
                collection.update_one(
                    {'_id': item_id},
                    {'$set': {'auctions': auctions}}
                )


"""
collection.find_one_and_update(
                filter={'_id': item_id},
                upsert=True,
                update={'$addToSet': {'auctions': auctions}}
            )
"""


test_document = {
    "realm_id": "510",
    "auctions": {
        "168645": [
            {
                "id": 1500391527,
                "quantity": 292,
                "unit_price": 250000,
                "time_left": "SHORT"
            },
            {
                "id": 1500401697,
                "quantity": 13,
                "unit_price": 200000,
                "time_left": "SHORT"
            },
            {
                "id": 1500449731,
                "quantity": 160,
                "unit_price": 100000,
                "time_left": "LONG"
            },
            {
                "id": 1500426842,
                "quantity": 26,
                "unit_price": 14500,
                "time_left": "MEDIUM"
            },
            {
                "id": 1500984425,
                "quantity": 70,
                "unit_price": 19600,
                "time_left": "VERY_LONG"
            },
            {
                "id": 1501143834,
                "quantity": 21,
                "unit_price": 19600,
                "time_left": "VERY_LONG"
            },
        ]
    }
}


def main():
    atlas_store = AtlasStore()
    atlas_store.insert_report(test_document)
    return 0


if __name__ == '__main__':
    sys.exit(main())
