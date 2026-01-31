import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Chakravyuh-OSINT/1.0)"
}

TIMEOUT = 5

# OSINT-safe username endpoints
USERNAME_SITES = {
    "GitHub": "https://github.com/{}",
    "GitLab": "https://gitlab.com/{}",
    "Bitbucket": "https://bitbucket.org/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "Dev.to": "https://dev.to/{}",
    "Kaggle": "https://www.kaggle.com/{}",
    "StackOverflow": "https://stackoverflow.com/users/{}",
    "DockerHub": "https://hub.docker.com/u/{}",
    "Pastebin": "https://pastebin.com/u/{}",
    "PyPI": "https://pypi.org/user/{}",
    "npm": "https://www.npmjs.com/~{}"
}


def discover_username(username: str):
    found = []
    checked = []

    for site, pattern in USERNAME_SITES.items():
        url = pattern.format(username)
        checked.append(site)

        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code == 200:
                found.append({
                    "site": site,
                    "url": url,
                    "confidence": "MEDIUM",
                    "evidence": "Public profile endpoint responded with HTTP 200"
                })

        except Exception:
            continue

    return {
        "username": username,
        "sites_found": found,
        "total_found": len(found),
        "sites_checked": checked
    }