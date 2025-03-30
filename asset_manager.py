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


PAPER_FILE = "paper_total_asset.json"

def get_paper_asset():
    if not os.path.exists(PAPER_FILE) or os.path.getsize(PAPER_FILE) == 0:
        return 10000  # 초기 가상 자산 기본값 (필요시 사용자 입력으로 확장 가능)
    with open(PAPER_FILE, "r") as f:
        return json.load(f)["total"]

def update_paper_asset(profit):
    total = get_paper_asset() + int(profit)
    with open(PAPER_FILE, "w") as f:
        json.dump({"total": total}, f)
    return total