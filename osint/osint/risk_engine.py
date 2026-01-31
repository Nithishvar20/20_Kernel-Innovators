from osint.ai_explainer import explain_reason
from osint.ml_ai_detector import predict_risk_ml


def calculate_risk(data):
    """
    Hybrid AI Risk Engine:
    - Rule-based OSINT scoring (transparent)
    - ML model for final risk classification
    - AI explanations for causes + mitigation
    """

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
                f"due to platform restrictions"
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

    # ================= IMAGE / MEDIA OSINT =================
    media_score = 0
    image_meta = data.get("image_metadata")

    if isinstance(image_meta, dict) and image_meta:
        media_score += 15
        score += 15

        if "Make" in image_meta or "Model" in image_meta:
            reasons.append("Image metadata reveals device make/model")

        if "DateTimeOriginal" in image_meta:
            reasons.append("Image metadata reveals capture timestamp")

        if "gps" in image_meta:
            reasons.append("Image metadata contains precise GPS location")

    # ================= TEXT OSINT =================
    text_score = 0
    text_risk = data.get("text_risk")

    if isinstance(text_risk, dict) and text_risk:
        text_score = text_risk.get("risk", 0)
        score += text_score
        reasons.extend(text_risk.get("findings", []))

    # ================= VIDEO OSINT =================
    video_risk = data.get("video_risk")
    if isinstance(video_risk, dict) and video_risk:
        media_score += video_risk.get("risk", 0)
        score += video_risk.get("risk", 0)
        reasons.extend(video_risk.get("signals", []))

    # ================= AUDIO OSINT =================
    audio_risk = data.get("audio_risk")
    if isinstance(audio_risk, dict) and audio_risk:
        media_score += audio_risk.get("risk", 0)
        score += audio_risk.get("risk", 0)
        reasons.extend(audio_risk.get("signals", []))

    # ================= INCONCLUSIVE HANDLING =================
    if inconclusive:
        reasons.append(
            "Some platforms could not be fully assessed due to access restrictions"
        )

    # ================= SCORE CAP =================
    score = min(score, 100)

    # ================= ML FEATURE VECTOR =================
    ml_features = {
        "platform_count": platform_count,

        "high_confidence_accounts": sum(
            1 for p in platforms.values()
            if p.get("confidence") == "HIGH"
        ),

        "private_profiles": sum(
            1 for p in platforms.values()
            if p.get("visibility") == "PRIVATE"
        ),

        "image_metadata": 1 if image_meta else 0,

        "media_risk": media_score,

        "text_risk": text_score,

        "identity_correlation": identity_score,
    }

    # ================= REAL AI MODEL =================
    ml_result = predict_risk_ml(ml_features)

    # ================= FINAL RISK LEVEL (ML WINS) =================
    final_level = ml_result["level"]

    # ================= RISK BREAKDOWN =================
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
        "score": ml_result["score"],
        "level": final_level,
        "reasons": reasons,
        "ai_explanations": ai_explanations,
        "platform_breakdown": platform_breakdown,
        "risk_breakdown": risk_breakdown,
        "ml_confidence": ml_result["confidence"],
        "inconclusive_platforms": inconclusive,
        "confidence": (
            "Risk classification is generated using a trained machine learning model "
            "combined with explainable OSINT heuristics. No private or restricted data "
            "sources are used."
        )
    }