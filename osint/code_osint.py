import re

API_KEY_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',     # AWS
    r'AIza[0-9A-Za-z\\-_]{35}'  # Google
]

def scan_code(text):
    leaks = []
    for pattern in API_KEY_PATTERNS:
        leaks += re.findall(pattern, text)

    return {
        "api_keys_found": bool(leaks),
        "count": len(leaks),
        "risk": "HIGH" if leaks else "LOW"
    }