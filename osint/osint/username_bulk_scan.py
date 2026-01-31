import json
import requests
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 5

BASE_DIR = Path(__file__).resolve().parent.parent
PLATFORM_DIR = BASE_DIR / "data" / "platforms"


def load_platforms(filename):
    path = PLATFORM_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def scan_platform(username, platform_name, cfg, tier):
    url = cfg["url"].replace("{username}", username)

    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        page = r.text.lower()

        # relaxed logic for bulk platforms
        found = False

        if r.status_code == 200:
            if "failure" in cfg:
                if any(f.lower() in page for f in cfg["failure"]):
                    found = False
                else:
                    found = username.lower() in page
            else:
                found = username.lower() in page

        return {
            "platform": platform_name,
            "url": url,
            "status": "FOUND" if found else "NOT FOUND",
            "confidence": "LOW" if found else "UNKNOWN",
            "tier": tier,
            "evidence": "Bulk discovery check"
        }

    except Exception as e:
        return {
            "platform": platform_name,
            "url": url,
            "status": "ERROR",
            "confidence": "UNKNOWN",
            "tier": tier,
            "evidence": str(e)
        }


def bulk_username_scan(username):
    """
    Scans Tier-2 and Tier-3 platforms (970+)
    """
    results = {}

    tier2 = load_platforms("tier2.json")
    tier3 = load_platforms("tier3.json")

    for name, cfg in tier2.items():
        results[name] = scan_platform(username, name, cfg, tier=2)

    for name, cfg in tier3.items():
        results[name] = scan_platform(username, name, cfg, tier=3)

    return results