from multiprocessing.connection import Client
import boto3 
from botocore.exceptions import ClientError
import json
import sys
from pathlib import Path

class DynamoStore:
    def __init__(self) -> None:
        self.db = boto3.resource('dynamodb')
        self.table = None
        self.load_table()


    def load_table(self) -> None:
        try:
            table = self.db.Table('auctions')
            table.load()
            self.table = table
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Creating table...")
                self.table = self.db.create_table(
                    TableName='auctions',
                    KeySchema=[
                        {'AttributeName': 'realm_id', 'KeyType': 'HASH'},
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": 'realm_id', "AttributeType": 'N'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
                )
                self.table.wait_until_exists()
            else:
                print(e)
                sys.exit(1)

    def add_auction(self, auction):
        try:
            self.table.put_item(Item=auction)
        except ClientError as e:
            print(e)


def load_cached_auctions():
    for path in Path('auctioncached').glob('*.json'):
        with path.open() as f:
            yield json.load(f)


def main():
    store = DynamoStore()
    for auction_report in load_cached_auctions():
        store.add_auction(auction_report)

if __name__ == "__main__":
    sys.exit(main())