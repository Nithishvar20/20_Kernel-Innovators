import json
import os

# Absolute path fix
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE = os.path.join(DATA_DIR, "scans.json")

def save_scan(data):
    # Ensure data folder exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # Create file if not exists
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump([], f)

    with open(FILE, "r") as f:
        scans = json.load(f)

    scans.append(data)

    with open(FILE, "w") as f:
        json.dump(scans, f, indent=2)

def compare_last_scan(current):
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        scans = json.load(f)

    if not scans:
        return []

    last = scans[-1].get("platforms_found", {})
    return [p for p in current.get("platforms_found", {}) if p not in last]