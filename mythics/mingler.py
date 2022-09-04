import json
from pathlib import Path

def load_runs():
    cache = Path(f"mythics/cache")
    for file_path in cache.glob("*/*/*.json"):
        with file_path.open("r") as f:
            yield json.load(f), file_path.parent.parent.name

def extract_features(run_data):
    feature_table = []
    for group in run_data["leading_groups"]:
        members = {f"player-{index}": player["profile"]["id"] for index, player in enumerate(group["members"])} 
        feature_table.append(members)    
    return feature_table

def cache_features(feature_table, run, server_id):
    Path(f"mythics/features").mkdir(parents=True, exist_ok=True)
    output_path = Path(f"mythics/features/{server_id}_{run['map']['id']}_{run['period']}.json")
    with output_path.open("w+") as f:
        json.dump(feature_table, f, indent=4)

def main():
    for run, server_id in load_runs():
        run_features = extract_features(run)

        cache_features(run_features, run, server_id)

if __name__ == "__main__":
    import sys
    sys.exit(main())