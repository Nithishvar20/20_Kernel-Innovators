def scan_repo_text(text):
    leaks = []

    keywords = ["api_key", "secret", "token", "password"]
    for k in keywords:
        if k in text.lower():
            leaks.append(f"Potential secret keyword: {k}")

    return {
        "risk": len(leaks) * 10,
        "findings": leaks
    }