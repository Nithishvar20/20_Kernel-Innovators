import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 5


def scan_username(username: str):
    platforms_found = {}
    inconclusive = set()

    def safe_get(url):
        return requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    # =========================================================
    # GITHUB — HIGH RELIABILITY
    # =========================================================
    try:
        url = f"https://github.com/{username}"
        r = safe_get(url)
        page = r.text.lower()

        if r.status_code == 200 and "repositories" in page and "page not found" not in page:
            platforms_found["GitHub"] = {
                "url": url,
                "confidence": "HIGH",
                "visibility": "PUBLIC",
                "richness": "LOW",
                "evidence": "Public GitHub profile detected (technical data only)"
            }
    except:
        pass

    # =========================================================
    # LINKEDIN — LOGIN WALLED
    # =========================================================
    try:
        url = f"https://www.linkedin.com/in/{username}"
        r = safe_get(url)
        page = r.text.lower()

        if (
            r.status_code == 200
            and "experience" in page
            and "education" in page
            and "sign in" not in page
        ):
            platforms_found["LinkedIn"] = {
                "url": url,
                "confidence": "LOW",
                "visibility": "PUBLIC",
                "richness": "LOW",
                "evidence": "Public LinkedIn sections visible without login"
            }
        else:
            inconclusive.add("LinkedIn")
    except:
        inconclusive.add("LinkedIn")

    # =========================================================
    # INSTAGRAM — OSINT-SAFE (NO FALSE LABELS)
    # =========================================================
    try:
        url = f"https://www.instagram.com/{username}/"
        r = safe_get(url)
        page = r.text.lower()

        not_found = [
            "profile isn't available",
            "sorry, this page isn't available",
            "the link you followed may be broken",
            "page not found"
        ]

        exists = (
            r.status_code == 200
            and '"username"' in page
            and '"profilepage_' in page
            and not any(x in page for x in not_found)
        )

        if exists:
            post_count = page.count('"shortcode"')

            private_signals = [
                '"is_private":true',
                "this account is private",
                "follow to see their photos",
                "only approved followers"
            ]

            if any(p in page for p in private_signals):
                visibility = "PRIVATE"
                evidence = "Instagram account exists but content is private"
            elif post_count > 0:
                visibility = "PUBLIC"
                evidence = "Public Instagram profile with visible posts"
            else:
                visibility = "EXISTS (VISIBILITY UNKNOWN)"
                evidence = "Instagram account exists but visibility could not be reliably determined"

            platforms_found["Instagram"] = {
                "url": url,
                "confidence": "HIGH",
                "visibility": visibility,
                "richness": (
                    "HIGH" if post_count > 20 else
                    "MEDIUM" if post_count > 5 else
                    "LOW"
                ),
                "evidence": evidence
            }

    except:
        pass

    
    # =========================================================
    # FACEBOOK — HIGH FALSE POSITIVE RISK
    # =========================================================
    try:
        url = f"https://www.facebook.com/{username}"
        r = safe_get(url)
        page = r.text.lower()

        blockers = [
            "this content isn't available",
            "content not available",
            "log in to facebook",
            "create new account",
            "page not found",
            "go to feed"
        ]

        strong = all(x in page for x in ["timeline", "friends", "photos"])

        if r.status_code == 200 and strong and not any(b in page for b in blockers):
            post_count = page.count("post")

            platforms_found["Facebook"] = {
                "url": url,
                "confidence": "LOW",
                "visibility": "PUBLIC",
                "richness": (
                    "HIGH" if post_count > 20 else
                    "MEDIUM" if post_count > 5 else
                    "LOW"
                ),
                "evidence": "Public Facebook timeline with visible sections"
            }
        else:
            inconclusive.add("Facebook")
    except:
        inconclusive.add("Facebook")

    # =========================================================
    # THREADS
    # =========================================================
    try:
        url = f"https://www.threads.net/@{username}"
        r = safe_get(url)
        page = r.text.lower()

        if (
            r.status_code == 200
            and "threads" in page
            and "page not found" not in page
            and "log in" not in page
        ):
            platforms_found["Threads"] = {
                "url": url,
                "confidence": "MEDIUM",
                "visibility": "PUBLIC",
                "richness": "MEDIUM",
                "evidence": "Public Threads profile detected"
            }
    except:
        pass

    # =========================================================
    # REDDIT
    # =========================================================
    try:
        url = f"https://www.reddit.com/user/{username}"
        r = safe_get(url)
        page = r.text.lower()

        if (
            r.status_code == 200
            and "karma" in page
            and "this user has been suspended" not in page
        ):
            platforms_found["Reddit"] = {
                "url": url,
                "confidence": "HIGH",
                "visibility": "PUBLIC",
                "richness": "HIGH",
                "evidence": "Public Reddit activity detected"
            }
    except:
        pass

    return {
        "platforms_found": platforms_found,
        "inconclusive_platforms": sorted(inconclusive)
    }