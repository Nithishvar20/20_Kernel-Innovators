def calculate_reverse_risk(engagement):
    score = engagement.get("exposure_score", 0)

    if score < 200:
        return {
            "level": "Low",
            "reason": "Limited engagement and low redistribution likelihood"
        }
    elif score < 450:
        return {
            "level": "Medium",
            "reason": "Moderate public exposure across multiple platforms"
        }
    else:
        return {
            "level": "High",
            "reason": "High engagement and strong redistribution signals"
        }
