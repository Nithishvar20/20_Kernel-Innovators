from osint.ai_explainer import explain_reason


def calculate_risk(data):
    score = 0
    reasons = []
    platform_breakdown = []

    platforms = data.get("platforms_found", {}) or {}
    inconclusive = data.get("inconclusive_platforms", []) or []

    # ================= PLATFORM BASE WEIGHTS =================
    PLATFORM_BASE = {
        "GitHub": 5,
        "LinkedIn": 5,
        "Instagram": 10,
        "Facebook": 15,
        "Threads": 10,
        "Reddit": 25,
    }

    RICHNESS_MULTIPLIER = {
        "LOW": 0.5,
        "MEDIUM": 1.0,
        "HIGH": 1.4,
    }

    # ================= PER-PLATFORM SCORING =================
    for platform, info in platforms.items():
        if not isinstance(info, dict):
            continue

        base = PLATFORM_BASE.get(platform, 5)
        visibility = info.get("visibility", "PUBLIC")
        richness = info.get("richness", "LOW")

        if visibility == "PRIVATE":
            platform_score = int(base * 0.4)
            reasons.append(
                f"{platform}: Account exists but content is private, limiting public exposure"
            )

        elif visibility == "EXISTS (VISIBILITY UNKNOWN)":
            platform_score = int(base * 0.3)
            reasons.append(
                f"{platform}: Account exists but visibility could not be reliably determined "
                f"due to platform access restrictions"
            )

        else:
            multiplier = RICHNESS_MULTIPLIER.get(richness, 0.5)
            platform_score = int(base * multiplier)
            reasons.append(
                f"{platform}: Public profile with {richness.lower()} information exposure"
            )

        score += platform_score

        platform_breakdown.append({
            "platform": platform,
            "score": platform_score,
            "base": base,
            "visibility": visibility,
            "richness": richness
        })

    # ================= IDENTITY CORRELATION =================
    platform_count = len(platforms)

    identity_score = 0
    if platform_count >= 2:
        identity_score += 10
        score += 10
        reasons.append(
            "Same identifier reused across multiple platforms, enabling identity correlation"
        )

    if platform_count >= 4:
        identity_score += 10
        score += 10
        reasons.append(
            "Broad cross-platform presence increases profiling and tracking risk"
        )

    # ================= IMAGE OSINT =================
    image_meta = data.get("image_metadata")
    media_score = 0

    if isinstance(image_meta, dict) and image_meta:
        score += 15
        media_score += 15

        if "Make" in image_meta or "Model" in image_meta:
            reasons.append("Image metadata reveals device make/model")

        if "DateTimeOriginal" in image_meta:
            reasons.append("Image metadata reveals capture timestamp")

        if "gps" in image_meta:
            reasons.append("Image metadata contains precise GPS location")

    # ================= TEXT OSINT =================
    text_risk = data.get("text_risk")
    text_score = 0

    if isinstance(text_risk, dict) and text_risk:
        text_score = text_risk.get("risk", 0)
        score += text_score
        reasons.extend(text_risk.get("findings", []))

    # ================= GEO OSINT =================
    geo_risk = data.get("geo_risk")
    if isinstance(geo_risk, dict) and geo_risk:
        score += geo_risk.get("risk", 0)
        media_score += geo_risk.get("risk", 0)
        if geo_risk.get("evidence"):
            reasons.append(geo_risk.get("evidence"))

    # ================= VIDEO OSINT =================
    video_risk = data.get("video_risk")
    if isinstance(video_risk, dict) and video_risk:
        score += video_risk.get("risk", 0)
        media_score += video_risk.get("risk", 0)
        reasons.extend(video_risk.get("signals", []))

    # ================= AUDIO OSINT =================
    audio_risk = data.get("audio_risk")
    if isinstance(audio_risk, dict) and audio_risk:
        score += audio_risk.get("risk", 0)
        media_score += audio_risk.get("risk", 0)
        reasons.extend(audio_risk.get("signals", []))

    # ================= INCONCLUSIVE =================
    if inconclusive:
        reasons.append(
            "Some platforms could not be fully assessed due to access restrictions; "
            "actual exposure may be higher"
        )

    # ================= SCORE CAP =================
    score = min(score, 100)

    # ================= RISK LEVEL =================
    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # ================= CONFIDENCE SCORE =================
    confidence_score = min(
        (platform_count * 15)
        + (20 if image_meta else 0)
        + (15 if text_risk else 0)
        + (10 if video_risk else 0)
        + (10 if audio_risk else 0),
        100
    )

    # ================= RISK BREAKDOWN BY CATEGORY =================
    breakdown = {
        "platform_exposure": sum(p["score"] for p in platform_breakdown),
        "identity_correlation": identity_score,
        "media_metadata": media_score,
        "text_content": text_score
    }

    risk_breakdown = {
        k: int((v / score) * 100) if score > 0 else 0
        for k, v in breakdown.items()
    }

    # ================= AI EXPLANATIONS =================
    ai_explanations = [
        {"reason": r, "explanation": explain_reason(r)}
        for r in reasons
    ]

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "ai_explanations": ai_explanations,
        "platform_breakdown": platform_breakdown,
        "risk_breakdown": risk_breakdown,
        "inconclusive_platforms": inconclusive,
        "confidence_score": confidence_score,
        "confidence": (
            "Risk score is derived using explainable AI logic over publicly accessible "
            "OSINT signals. No private, paid, or restricted data sources are accessed."
        )
    }