def explain(prediction: dict):
    explanations = []

    score = prediction.get("score", 0)
    verdict = prediction.get("verdict", "")

    if score > 70:
        explanations.append(
            "The model detected strong visual patterns commonly associated with AI-generated images, "
            "such as unnatural textures, overly smooth regions, or synthetic noise artifacts."
        )

    elif score >= 50:
        explanations.append(
            "The image shows a mix of real and synthetic characteristics. Some AI-related artifacts "
            "are present, but not strongly enough to confirm with high confidence."
        )

    else:
        explanations.append(
            "The image appears consistent with real camera-captured photos, including natural noise, "
            "realistic lighting, and absence of synthetic generation artifacts."
        )

    # Optional confidence note
    explanations.append(
        f"Final verdict: {verdict}. Confidence is derived from a deep learning model trained on "
        "real vs AI-generated images."
    )

    return explanations