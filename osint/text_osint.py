def analyze_text(text):
    findings = []

    risk = 0

    keywords = {
        "phone": 5,
        "email": 5,
        "address": 10,
        "college": 5,
        "school": 5,
        "dob": 10,
        "location": 5,
        "city": 5
    }

    text_lower = text.lower()

    for word, weight in keywords.items():
        if word in text_lower:
            findings.append(f"Text contains potential personal identifier: '{word}'")
            risk += weight

    return {
        "risk": min(risk, 25),   # cap text risk
        "findings": findings
    }