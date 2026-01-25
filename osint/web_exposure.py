import requests
import dns.resolver
from urllib.parse import urlparse

# ================= CONFIG =================

HEADERS = {
    "User-Agent": "Chakravyuh-OSINT/1.0"
}

TIMEOUT = 5

# Truly sensitive if exposed
SENSITIVE_FILES = [
    ".env",
    ".git/config",
    "backup.zip",
    "db.sql",
    "config.php"
]

# Interesting but not vulnerabilities by default
INTERESTING_DIRS = [
    "admin",
    "login",
    "uploads",
    "backup"
]

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

# ================= HELPERS =================

def normalize_url(target: str) -> str:
    if not target.startswith("http"):
        target = "https://" + target
    return target.rstrip("/")


# ================= PATH CHECKS =================

def check_exposed_paths(base_url):
    exposed_sensitive = []
    interesting_paths = []

    for path in SENSITIVE_FILES + INTERESTING_DIRS:
        try:
            url = f"{base_url}/{path}"
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

            if r.status_code == 200 and len(r.text) > 50:
                if path in SENSITIVE_FILES:
                    exposed_sensitive.append(url)
                else:
                    interesting_paths.append(url)

        except Exception:
            pass

    return exposed_sensitive, interesting_paths


# ================= ROBOTS =================

def check_robots(base_url):
    disallowed = []
    sitemap = None

    try:
        r = requests.get(f"{base_url}/robots.txt", headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            for line in r.text.splitlines():
                line = line.strip()
                if line.lower().startswith("disallow"):
                    disallowed.append(line.split(":", 1)[1].strip())
                elif line.lower().startswith("sitemap"):
                    sitemap = line.split(":", 1)[1].strip()
    except Exception:
        pass

    return {
        "disallowed_paths": disallowed,
        "sitemap": sitemap
    }


# ================= SECURITY HEADERS =================

def check_security_headers(base_url):
    present = []
    missing = []

    try:
        r = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        for header in SECURITY_HEADERS:
            if header in r.headers:
                present.append(header)
            else:
                missing.append(header)
    except Exception:
        pass

    return {
        "present": present,
        "missing": missing
    }


# ================= DNS OSINT =================

def dns_osint(domain):
    records = {}

    for rtype in ["A", "MX", "TXT"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [str(r) for r in answers]
        except Exception:
            records[rtype] = []

    return records


# ================= RISK ENGINE =================

def calculate_web_risk(exposed, interesting, robots, headers):
    score = 0
    reasons = []

    # 🔴 Critical exposure
    if exposed:
        score += 70
        reasons.append("Publicly accessible sensitive files detected")

    # 🟠 Interesting directories (context only)
    if interesting:
        score += 10
        reasons.append("Interesting directories publicly accessible")

    # 🟡 robots.txt (informational only)
    if robots["disallowed_paths"]:
        score += 5
        reasons.append("robots.txt reveals restricted paths")

    # 🟡 Security headers
    missing_headers = len(headers["missing"])
    if missing_headers >= 4:
        score += 20
        reasons.append("Multiple security headers missing")
    elif missing_headers >= 2:
        score += 10
        reasons.append("Some security headers missing")

    # Final level
    if score >= 70:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }


# ================= MAIN ANALYSIS =================

def analyze_website_exposure(target):
    base_url = normalize_url(target)
    domain = urlparse(base_url).netloc

    exposed, interesting = check_exposed_paths(base_url)
    robots = check_robots(base_url)
    headers = check_security_headers(base_url)
    dns_records = dns_osint(domain)

    risk = calculate_web_risk(
        exposed=exposed,
        interesting=interesting,
        robots=robots,
        headers=headers
    )

    return {
        "target": base_url,
        "exposed_sensitive_files": exposed,
        "interesting_paths": interesting,
        "robots": robots,
        "security_headers": headers,
        "dns_records": dns_records,
        "risk": risk
    }