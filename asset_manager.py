import json
import os

FILE = "total_asset.json"

def get_total_asset():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({"total": 10_000_000}, f)
    with open(FILE, "r") as f:
        return json.load(f)["total"]

def update_total_asset(profit):
    total = get_total_asset() + int(profit)
    with open(FILE, "w") as f:
        json.dump({"total": total}, f)
    return total