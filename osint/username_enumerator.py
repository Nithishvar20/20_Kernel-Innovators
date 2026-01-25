import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 6


# ============================================================
# PLATFORM DEFINITIONS (STRONG OSINT MARKERS)
# ============================================================

SITES = {
    "GitHub": {
        "url": "https://github.com/{username}",
        "success": ["repositories", "followers", "following"],
        "failure": ["not found", "there isn’t a github pages site here"]
    },

    "Instagram": {
        "url": "https://www.instagram.com/{username}/",
        "success": ['"username"', '"profilepage_"'],
        "failure": [
            "sorry, this page isn't available",
            "the link you followed may be broken",
            "page isn't available"
        ]
    },

    "Twitter / X": {
        "url": "https://x.com/{username}",
        "success": [
            '"screen_name"',
            '"profile_image_url"',
            '"followers_count"'
        ],
        "failure": [
            "this account doesn’t exist",
            "this account doesn't exist",
            "try searching for another",
            "account suspended"
        ]
    },

    "Reddit": {
        "url": "https://www.reddit.com/user/{username}",
        "success": ["karma", "cake day"],
        "failure": [
            "page not found",
            "this user has been suspended",
            "nobody on reddit goes by that name"
        ]
    },

    "Pinterest": {
        "url": "https://www.pinterest.com/{username}/",
        "success": [
            '"username"',
            '"profile-followers"',
            '"profile-following"'
        ],
        "failure": [
            "couldn't find",
            "showing results for",
            "search results",
            "people named"
        ]
    },

    "Medium": {
        "url": "https://medium.com/@{username}",
        "success": [
            "followers",
            "member since",
            "medium.com/@"
        ],
        "failure": [
            "page not found",
            "404"
        ]
    },

    "Dev.to": {
        "url": "https://dev.to/{username}",
        "success": [
            "posts",
            "joined",
            "dev.to/"
        ],
        "failure": [
            "not found",
            "404"
        ]
    }
}


# ============================================================
# CORE ENUMERATION FUNCTION
# ============================================================

def enumerate_username(username: str):
    """
    OSINT-safe username enumeration using platform-specific
    fingerprinting to reduce false positives.
    """
    results = {}

    for platform, cfg in SITES.items():
        url = cfg["url"].format(username=username)

        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            page = r.text.lower()

            success = any(marker.lower() in page for marker in cfg["success"])
            failure = any(marker.lower() in page for marker in cfg["failure"])

            if r.status_code == 200 and success and not failure:
                results[platform] = {
                    "url": url,
                    "status": "FOUND",
                    "confidence": "HIGH",
                    "visibility": "PUBLIC",
                    "evidence": "Platform-specific profile markers detected"
                }
            else:
                results[platform] = {
                    "url": url,
                    "status": "NOT FOUND",
                    "confidence": "LOW",
                    "visibility": "UNKNOWN",
                    "evidence": "No reliable profile indicators found"
                }

        except requests.RequestException as e:
            results[platform] = {
                "url": url,
                "status": "ERROR",
                "confidence": "UNKNOWN",
                "visibility": "UNKNOWN",
                "evidence": f"Request failed: {str(e)}"
            }

    return results


# ============================================================
# OPTIONAL: QUICK CLI TEST
# ============================================================

if __name__ == "__main__":
    username = input("Enter username to enumerate: ").strip()
    results = enumerate_username(username)

    for platform, data in results.items():
        print(f"\n[{platform}]")
        for k, v in data.items():
            print(f"{k}: {v}")