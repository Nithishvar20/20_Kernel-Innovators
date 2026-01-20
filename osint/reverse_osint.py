
import requests

TRACKERS = ["google-analytics", "facebook", "doubleclick"]

def detect_trackers(url):
    found = []
    try:
        r = requests.get(url, timeout=5)
        for t in TRACKERS:
            if t in r.text.lower():
                found.append(t)
    except:
        pass
    return found
