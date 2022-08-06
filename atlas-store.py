import json
import pymongo
import sys
import os
from pathlib import Path

class AtlasStore:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient(f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PWD')}@cluster0.k0kxo.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client['auctions']

    def insert_report(self, report: dict) -> None:
        realm = report['realm_id']
        collection = self.db[realm]
        for item_id, auctions in report['auctions'].items():
            item_document = collection.find_one({'_id': item_id})
            print("doc", item_document)
            
            
            
            """
            collection.find_one_and_update(
                filter={'_id': item_id}, 
                upsert=True,
                update={'$addToSet': {'auctions': auctions}}               
            )
            """
            
         
                


def load_auction_reports():
    for path in Path("AuctionsProcessed").glob("*.json"):
        print(f"loading {path}")
        with open(path) as f:
            yield json.load(f)





def main():
    atlas_store = AtlasStore()
    for report in load_auction_reports():
        atlas_store.insert_report(report)

    return 0


if __name__ == '__main__':
    sys.exit(main())