import requests
import json
import sys
import os
from datetime import datetime
from pathlib import Path

class WowApi:
    def __init__(self, region="eu") -> None:
        self.region = region
        self.blizzard = f"https://{self.region}.api.blizzard.com"
        self.battlenet = f"https://{self.region}.battle.net"
        self.token = None 
        self.authenticate()

    def authenticate(self):
        req_params = {
            "url": f"{self.battlenet}/oauth/token",
            "headers": {
                "Authorization": f"Basic {os.environ['BASIC_AUTH']}"
            },
            "data":{
                'grant_type': 'client_credentials'
            },
            "files": [],
            "method": "POST"
        }

        response = requests.request(**req_params)
        try:
            response.raise_for_status()
            self.token = response.json()['access_token']

        except Exception as e:
            print(e)
            print(response.text)
            sys.exit(1)


    def get_connected_real_index(self):
        req_params = {
            "url": f"{self.blizzard}/data/wow/connected-realm/index",
            "headers": {
                "Authorization": f"Bearer {self.token}"
            },
            "params": {
                "namespace": f"dynamic-{self.region}"
            },
            "method": "GET"
        }

        response = requests.request(**req_params)
        try:
            response.raise_for_status()
            realms_ids = []
            for realm in response.json()['connected_realms']:
                realm_url, realm_params = realm['href'].split('?')
                realm_id = realm_url.split('/')[-1]
                realms_ids.append(realm_id)
            return realms_ids

        except Exception as e:
            print(e)
            print(response.text)
            sys.exit(1)        


    def get_auction_report(self, realm_id):
        req_params = {
            "url": f"{self.blizzard}/data/wow/connected-realm/{realm_id}/auctions",
            "headers": {
                "Authorization": f"Bearer {self.token}"
            },
            "params": {
                "namespace": f"dynamic-{self.region}"
            },
            "method": "GET"
        }

        response = requests.request(**req_params)
        try:
            response.raise_for_status()
            return response.json()['auctions']

        except Exception as e:
            print(e)
            print(response.text)
            sys.exit(1)

def main():
    client = WowApi()
    for realm_id in client.get_connected_real_index():
        print(f"getting report for realm {realm_id}")
        auctions = client.get_auction_report(realm_id)
        report = {
            "realm_id": realm_id,
            "timestamp": datetime.now().isoformat(),
            "auctions": auctions
        }
        with Path(f"auctioncached/{realm_id}.json").open('w+') as f:
            json.dump(report, f, indent=4)

    return 0



if __name__ == '__main__':
    sys.exit(main())