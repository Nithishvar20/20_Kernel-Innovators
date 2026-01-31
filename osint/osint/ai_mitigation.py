def mitigation_advice(explanations):
    advice = []

    for e in explanations:
        if "username reused" in e.lower():
            advice.append("Use unique usernames per platform")
        if "metadata" in e.lower():
            advice.append("Strip metadata before uploading media")
        if "location" in e.lower():
            advice.append("Disable GPS tagging in camera settings")
        if "sensitive website files" in e.lower():
            advice.append("Remove public access to configuration files")

    return list(set(advice))