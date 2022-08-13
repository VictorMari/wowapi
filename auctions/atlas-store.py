import json
import pymongo
import sys
import os
from pathlib import Path
from pymongo import UpdateOne

class AtlasStore:
    def __init__(self) -> None:
        self.client = pymongo.MongoClient(f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PWD')}@cluster0.k0kxo.mongodb.net/?retryWrites=true&w=majority")
        self.db = self.client['auctions']

    def insert_report(self, report: dict) -> None:
        realm = report['realm_id']
        auctions = report['auctions']
        collection = self.db[realm]
        bulk_operations = []

        for item_id, auctions in auctions.items():
            operation = UpdateOne(
                filter={'_id': item_id},
                upsert=True,
                update=[{'$addFields': {'auctions': auctions}}]
            )
            bulk_operations.append(operation)

        bulk_results = collection.bulk_write(bulk_operations)
        print(f"Inserted {bulk_results.upserted_count} documents")
        print(f"Updated {bulk_results.modified_count} documents")
        print(f"matched_count: {bulk_results.matched_count}")
        print(f"modified_count: {bulk_results.modified_count}")
        #print(f"write erros: {bulk_results.writeErrors}")            
         
                


def load_auction_reports():
    for path in Path("auctions/AuctionsProcessed").glob("*.json"):
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