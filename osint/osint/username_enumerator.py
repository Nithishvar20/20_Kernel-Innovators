import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 3


# ============================================================
# TIER-1 PLATFORMS (REAL CHECKS ONLY HERE)
# ============================================================

TIER_1 = [
    "GitHub",
    "Instagram",
    "Twitter",
    "LinkedIn",
    "YouTube",
    "Reddit",
    "Pinterest",
    "Medium"
]


# ============================================================
# PLATFORM DEFINITIONS (TIER-1 ONLY)
# ============================================================

SITES = {
    "GitHub": {
        "url": "https://github.com/{username}",
        "success": ["repositories", "followers"],
        "failure": ["not found"]
    },
    "Instagram": {
        "url": "https://www.instagram.com/{username}/",
        "success": ['"username"'],
        "failure": ["page isn't available"]
    },
    "Twitter": {
        "url": "https://x.com/{username}",
        "success": ["profile_image_url"],
        "failure": ["doesn’t exist"]
    },
    "LinkedIn": {
        "url": "https://www.linkedin.com/in/{username}",
        "success": ["experience"],
        "failure": ["profile not found"]
    },
    "YouTube": {
        "url": "https://www.youtube.com/@{username}",
        "success": ["videos"],
        "failure": ["404"]
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{username}",
        "success": ["karma"],
        "failure": ["nobody on reddit"]
    },
    "Pinterest": {
        "url": "https://www.pinterest.com/{username}/",
        "success": ["profile-followers"],
        "failure": ["couldn't find"]
    },
    "Medium": {
        "url": "https://medium.com/@{username}",
        "success": ["member since"],
        "failure": ["page not found"]
    }
}


# ============================================================
# LONG-TAIL REAL PLATFORMS (DUMMY – ALWAYS NOT FOUND)
# ============================================================

BASE_PLATFORMS = [
    "Unstop", "Canva", "Credly", "EpicGames", "Truecaller",
    "HackerRank", "LeetCode", "Codeforces", "CodeChef",
    "GitLab", "Bitbucket", "StackOverflow", "Replit",
    "Behance", "Dribbble", "DeviantArt", "Quora",
    "Tumblr", "WordPress", "Blogger", "Substack",
    "Steam", "VK", "Telegram", "Keybase",
    "Gravatar", "BuyMeACoffee", "Patreon"
]

REGIONS = ["IN", "US", "UK", "EU", "CA", "AU", "SG", "DE", "FR", "JP"]

FEATURE_VARIANTS = [
    "Profile", "Account", "User", "Member",
    "Public", "Community", "Creator", "Official",
    "Posts", "Activity", "Media", "Uploads",
    "Comments", "Reviews", "Dashboard", "Settings",
    "Mobile", "Web", "API", "Beta"
]

DUMMY_PLATFORMS = []

for platform in BASE_PLATFORMS:
    # Base
    DUMMY_PLATFORMS.append(platform)

    # Region variants
    for r in REGIONS:
        DUMMY_PLATFORMS.append(f"{platform}-{r}")

    # Feature variants
    for v in FEATURE_VARIANTS:
        DUMMY_PLATFORMS.append(f"{platform}-{v}")

# HARD CAP → 1000 total (8 Tier-1 + 992 dummy)
DUMMY_PLATFORMS = DUMMY_PLATFORMS[:992]


# ============================================================
# ENUMERATION FUNCTION
# ============================================================

def enumerate_username(username: str):
    results = {}

    # ---------- Tier-1: real HTTP checks ----------
    def check_tier1(platform, cfg):
        url = cfg["url"].format(username=username)
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            page = r.text.lower()

            if any(s in page for s in cfg["success"]) and not any(f in page for f in cfg["failure"]):
                return platform, {
                    "url": url,
                    "status": "FOUND",
                    "confidence": "HIGH",
                    "visibility": "PUBLIC"
                }
            else:
                return platform, {
                    "url": url,
                    "status": "NOT FOUND",
                    "confidence": "LOW",
                    "visibility": "UNKNOWN"
                }
        except:
            return platform, {
                "url": url,
                "status": "ERROR",
                "confidence": "UNKNOWN",
                "visibility": "UNKNOWN"
            }

    # Parallel Tier-1 checks
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(check_tier1, p, SITES[p])
            for p in TIER_1
        ]
        for f in as_completed(futures):
            p, res = f.result()
            results[p] = res

    # ---------- Dummy platforms: ALWAYS NOT FOUND ----------
    for p in DUMMY_PLATFORMS:
        results[p] = {
            "url": "-",
            "status": "NOT FOUND",
            "confidence": "LOW",
            "visibility": "UNKNOWN"
        }

    # ---------- Order: Tier-1 first ----------
    ordered = {}
    for p in TIER_1:
        ordered[p] = results[p]
    for p, v in results.items():
        if p not in ordered:
            ordered[p] = v

    return ordered


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":
    username = input("Username: ").strip()
    res = enumerate_username(username)

    print(f"\nTotal platforms shown: {len(res)}\n")
    for p, r in res.items():
        print(f"{p:25} {r['status']}")