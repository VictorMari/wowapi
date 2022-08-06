import requests
import json
import sys
import os







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


def main():
    client = WowApi()
    return 0

if __name__ == '__main__':
    sys.exit(main())