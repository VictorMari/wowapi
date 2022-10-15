import json
from pathlib import Path

def load_runs():
    for run in Path("mythics/cache").glob("*.json"):
        with run.open("r") as f:
            yield run, json.load(f)

def extract_player_ids(run_data):
    runs = []
    for run in run_data["leading_groups"]:
        runs.append([player["profile"]["id"] for player in run["members"]])
    return runs

def main():
    for run, data in load_runs():
        run_features = extract_player_ids(data)
        with Path("mythics/features", run.name).open("w+") as f:
            print("saving", run.name)
            json.dump(run_features, f, indent=4)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())