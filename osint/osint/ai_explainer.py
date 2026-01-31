def explain_reason(reason: str):
    if "identity" in reason.lower():
        return "Avoid reusing the same username across platforms to reduce cross-platform correlation."
    if "public profile" in reason.lower():
        return "Restrict public visibility and remove unnecessary personal details."
    if "metadata" in reason.lower():
        return "Strip metadata from images before sharing online."
    if "private" in reason.lower():
        return "Private profiles reduce exposure but still confirm account existence."
    return "Review platform privacy and content exposure settings."