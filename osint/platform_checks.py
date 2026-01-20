import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (OSINT Research)"
}

TIMEOUT = 8


def instagram(username):
    url = f"https://www.instagram.com/{username}/"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    if r.status_code == 404:
        return None

    if "Sorry, this page isn't available" in r.text:
        return None

    if '"profilePage_' in r.text:
        return {
            "status": "CONFIRMED",
            "confidence": 0.9,
            "url": url,
            "richness": "HIGH",
            "evidence": "Instagram profile page markers found"
        }

    return {
        "status": "INCONCLUSIVE",
        "confidence": 0.4,
        "url": url,
        "richness": "LOW",
        "evidence": "Instagram page accessible but profile markers missing"
    }


def github(username):
    url = f"https://github.com/{username}"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    if r.status_code == 404:
        return None

    if "Not Found" in r.text:
        return None

    if 'itemprop="name"' in r.text:
        return {
            "status": "CONFIRMED",
            "confidence": 0.85,
            "url": url,
            "richness": "HIGH",
            "evidence": "GitHub profile metadata detected"
        }

    return {
        "status": "LIKELY",
        "confidence": 0.6,
        "url": url,
        "richness": "MEDIUM",
        "evidence": "GitHub page exists but metadata limited"
    }


def twitter(username):
    url = f"https://x.com/{username}"
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    if r.status_code == 404:
        return None

    if "This account doesn’t exist" in r.text:
        return None

    if "profile" in r.text.lower():
        return {
            "status": "LIKELY",
            "confidence": 0.65,
            "url": url,
            "richness": "MEDIUM",
            "evidence": "X profile page structure detected"
        }

    return None