import boto3 
import json
import sys
from pathlib import Path

class DynamoStore:
    pass


def load_cached_auctions():
    for path in Path('auctioncached').glob('*.json'):
        with path.open() as f:
            yield json.load(f)


def main():
    for auction in load_cached_auctions():
        print(len(auction['auctions']))


if __name__ == "__main__":
    sys.exit(main())