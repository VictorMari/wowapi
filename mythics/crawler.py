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
    print(realms_ids)
    cachePath = Path(f'mythics/cache')
    cachePath.mkdir(parents=True, exist_ok=True)

    for realm_id in realms_ids:
        realm_cache = cachePath.joinpath(f"{realm_id}")
        realm_cache.mkdir(parents=True, exist_ok=True)
        leaderboards = crawler.get_leaderboard_index(realm_id)
        for leaderboard in leaderboards['current_leaderboards']:
            href_link = leaderboard['key']['href']
            leaderboard_data = crawler.get_ref_url(href_link)
            # leaderboard metadata
            leaderboard_map_id = leaderboard_data["map"]['id']
            current_period = leaderboard_data["period"]
            dungeon_cache = realm_cache.joinpath(f"{leaderboard_map_id}")
            dungeon_cache.mkdir(parents=True, exist_ok=True)
            leaderboard_store_path = dungeon_cache.joinpath(f"{current_period}.json")
            with leaderboard_store_path.open('w+') as f:
                json.dump(leaderboard_data, f, indent=4)

    return 0

if __name__ == '__main__':
    sys.exit(main())
