def analyze_engagement_exposure(image_intel):
    base_likes = 50
    base_shares = 10
    base_comments = 5

    # Heuristics
    if image_intel.get("reuse_probability") == "High":
        base_likes += 120
        base_shares += 40
        base_comments += 25
    elif image_intel.get("reuse_probability") == "Medium":
        base_likes += 70
        base_shares += 25
        base_comments += 15

    engagement = {
        "estimated_likes": base_likes,
        "estimated_shares": base_shares,
        "estimated_comments": base_comments
    }

    engagement["exposure_score"] = (
        base_likes +
        base_shares * 3 +
        base_comments * 2
    )

    return engagement
