import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 5


def scan_username(username: str, platform: str | None = None):
    """
    OSINT-safe username scanner.
    Supported platforms: Instagram, Facebook, Threads
    """

    platforms_found = {}
    inconclusive = set()

    if not username:
        return {
            "platforms_found": {},
            "inconclusive_platforms": []
        }

    def safe_get(url):
        return requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    # =========================================================
    # INSTAGRAM
    # =========================================================
    def check_instagram(uname):
        try:
            url = f"https://www.instagram.com/{uname}/"
            r = safe_get(url)
            page = r.text.lower()

            not_found = [
                "profile isn't available",
                "sorry, this page isn't available",
                "page not found",
                "the link you followed may be broken"
            ]

            exists = (
                r.status_code == 200
                and '"username"' in page
                and not any(x in page for x in not_found)
            )

            if not exists:
                return None

            post_count = page.count('"shortcode"')

            private_signals = [
                '"is_private":true',
                "this account is private",
                "follow to see their photos",
            ]

            visibility = (
                "PRIVATE" if any(p in page for p in private_signals)
                else "PUBLIC"
            )

            return {
                "url": url,
                "confidence": "HIGH",
                "visibility": visibility,
                "richness": (
                    "HIGH" if post_count > 20 else
                    "MEDIUM" if post_count > 5 else
                    "LOW"
                ),
                "evidence": (
                    "Instagram account exists (private)"
                    if visibility == "PRIVATE"
                    else "Public Instagram profile with visible posts"
                )
            }

        except Exception:
            return None

    # =========================================================
    # FACEBOOK
    # =========================================================
    def check_facebook(uname):
        try:
            url = f"https://www.facebook.com/{uname}"
            r = safe_get(url)
            page = r.text.lower()

            blockers = [
                "log in to facebook",
                "this content isn't available",
                "page not found",
                "create new account",
            ]

            strong_signals = all(
                x in page for x in ["timeline", "friends", "photos"]
            )

            if r.status_code == 200 and strong_signals and not any(b in page for b in blockers):
                post_count = page.count("post")

                return {
                    "url": url,
                    "confidence": "LOW",
                    "visibility": "PUBLIC",
                    "richness": (
                        "HIGH" if post_count > 20 else
                        "MEDIUM" if post_count > 5 else
                        "LOW"
                    ),
                    "evidence": "Public Facebook timeline detected"
                }

            return None

        except Exception:
            return None

    # =========================================================
    # THREADS
    # =========================================================
    def check_threads(uname):
        try:
            url = f"https://www.threads.net/@{uname}"
            r = safe_get(url)
            page = r.text.lower()

            if (
                r.status_code == 200
                and "threads" in page
                and "page not found" not in page
                and "log in" not in page
            ):
                return {
                    "url": url,
                    "confidence": "MEDIUM",
                    "visibility": "PUBLIC",
                    "richness": "MEDIUM",
                    "evidence": "Public Threads profile detected"
                }

            return None

        except Exception:
            return None

    # =========================================================
    # PLATFORM DISPATCH
    # =========================================================
    checks = {
        "Instagram": check_instagram,
        "Facebook": check_facebook,
        "Threads": check_threads
    }

    # ---- Platform-wise scan ----
    if platform:
        checker = checks.get(platform)
        if checker:
            result = checker(username)
            if result:
                platforms_found[platform] = result
            else:
                inconclusive.add(platform)

    # ---- Single username scan ----
    else:
        for plat, checker in checks.items():
            result = checker(username)
            if result:
                platforms_found[plat] = result
            else:
                inconclusive.add(plat)

    return {
        "platforms_found": platforms_found,
        "inconclusive_platforms": sorted(inconclusive)
    }