def explain_reason(reason: str):
    """
    Generate an explainable AI-style explanation for a given risk reason.
    This is deterministic, transparent, and OSINT-safe.
    """

    r = reason.lower()

    if "private" in r:
        return (
            "The account exists, but privacy settings restrict public access. "
            "This limits direct exposure, though indirect association risks may still exist."
        )

    if "public profile" in r:
        return (
            "Publicly accessible profiles allow unrestricted data collection, "
            "making profiling and identity inference easier."
        )

    if "identity correlation" in r:
        return (
            "Using the same identifier across platforms enables cross-platform linkage, "
            "which significantly increases tracking and profiling risk."
        )

    if "cross-platform presence" in r or "profiling" in r:
        return (
            "A wide presence across multiple platforms increases the amount of "
            "information available for behavioral and identity analysis."
        )

    if "image metadata" in r or "exif" in r:
        return (
            "Image metadata may unintentionally reveal device details, timestamps, "
            "or geographic location, which can be exploited for tracking."
        )

    if "email" in r or "phone" in r:
        return (
            "Direct contact identifiers exposed publicly enable targeted attacks, "
            "spam campaigns, or social engineering attempts."
        )

    if "reddit" in r:
        return (
            "Reddit activity often reflects opinions, interests, and behavioral patterns "
            "that can be used for profiling."
        )

    if "could not be fully assessed" in r or "access restrictions" in r:
        return (
            "Platform restrictions limit public visibility, meaning actual exposure "
            "may be underestimated due to lack of verifiable signals."
        )

    # Default fallback explanation
    return (
        "This factor contributes to the overall exposure score based on "
        "public accessibility and correlation potential."
    )