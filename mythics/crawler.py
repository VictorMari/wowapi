import requests
import sys
import json
import time
from pathlib import Path

from requests.exceptions import Timeout
from requests.exceptions import ReadTimeout

class WowDataApi:
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
                "Authorization": "Basic ZjBlZmY1ODJiYTMwNGQyMjg4MWQ2NjRhYWYwMjI5ZjI6N0g3eFpIT1E2U2l0d3dpU2lzU3RjYnRLQ2R4Um9nQ1k=" #f"Basic {os.environ['BASIC_AUTH']}"
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
                "namespace": f"dynamic-{self.region}",
                "locale": "en_Gb"
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

    def get_leaderboard_index(self, realmId):
        req_params = {
            "url": f"{self.blizzard}/data/wow/connected-realm/{realmId}/mythic-leaderboard/index",
            "headers": {
                "Authorization": f"Bearer {self.token}"
            },
            "params": {
                "namespace": f"dynamic-{self.region}",
                "locale": "en_Gb"
            },
            "method": "GET"
        }

        response = requests.request(**req_params)
        try:
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(e)
            print(response.text)
            sys.exit(1)

    def get_ref_url(self, href):
        print("Getting leaderboard", href)
        req_params = {
            "url": href,
            "headers": {
                "Authorization": f"Bearer {self.token}"
            },
            "params": {
                "namespace": f"dynamic-{self.region}",
                "locale": "en_Gb"
            },
            "method": "GET",
            "timeout": 5
        }


        response = None
        try:
            response = requests.request(**req_params)
            response.raise_for_status()
            return response.json()

        except (Timeout, ReadTimeout) as e:
            print(e, "Well we got throttled, lets try again 😊")
            time.sleep(30)
            return self.get_ref_url(href)
        except Exception as e:
            print(e)
            if response:
                print(response.text)
            print(f"Retrying", href)
            time.sleep(30)
            return self.get_ref_url(href)
            



    

def main():
    crawler = WowDataApi()
    crawler.authenticate()
    realms_ids = crawler.get_connected_real_index()
    cachePath = Path(f'mythics/cache')
    cachePath.mkdir(parents=True, exist_ok=True)

    for realm_id in realms_ids:
        print("Getting leaderboard for", realm_id)
        leaderboards = crawler.get_leaderboard_index(realm_id)
        for leaderboard in leaderboards['current_leaderboards']:
            dungeon_leaderboard = crawler.get_ref_url(leaderboard["key"]['href'])
            leaderboard_map_id = leaderboard["id"]
            current_period = dungeon_leaderboard["period"]
            leaderboard_name = "_".join([realm_id, str(leaderboard_map_id), str(current_period)])
            leaderboard_path = cachePath.joinpath(f"{leaderboard_name}.json")
            print("Saving", leaderboard_path)
            if leaderboard_path.exists():
                print("Already exists, skipping")
                continue

            dungeon_leaderboard["dungeon_id"] = leaderboard_map_id
            with leaderboard_path.open('w+') as f:
                json.dump(dungeon_leaderboard, f, indent=4)

    return 0

if __name__ == '__main__':
    sys.exit(main())
