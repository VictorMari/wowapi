import json
from pathlib import Path

def load_old_cache():
    for file in Path("old-cache").glob("*/*/*.json"):
        yield file
        
def main():
    new_cache = Path("cache")
    new_cache.mkdir(exist_ok=True)
    for file in load_old_cache():
        with file.open("r") as f:
            run = json.load(f)
            server_id, dungeon_id, period = file.parts[-3:]
        with new_cache.joinpath(f"{server_id}_{dungeon_id}_{period}").open("w+") as f:
            json.dump(run, f, indent=4)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())