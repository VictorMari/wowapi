import json
import sys
from pathlib import Path


def load_auction_reports():
    for path in Path("auctions/auctioncached").glob("*.json"):
        print(f"loading {path}")
        with open(path) as f:
            yield json.load(f)
    

def aggregateAuctions(report):
    auction_table = {}
    for auction in report["auctions"]:
        item_id = auction["item"]["id"]
        auction_id = auction["id"]
        if item_id not in auction_table:
            auction_table[item_id] = {}
        del auction["item"]["id"]
        del auction["id"]
        if len(auction["item"].keys()) == 0:
            del auction["item"]

        auction_table[item_id][auction_id] = auction

    return auction_table



def main():
    Path("auctions/AuctionsProcessed").mkdir(parents=True, exist_ok=True)
    for report in load_auction_reports():
        ah_table = aggregateAuctions(report)
        report["auctions"] = ah_table
        with Path(f"auctions/AuctionsProcessed/{report['realm_id']}.json").open("w+") as f:
            json.dump(report, f, indent=4)

    return 0

if __name__ == '__main__':
    sys.exit(main())