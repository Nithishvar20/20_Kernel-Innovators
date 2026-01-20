import subprocess
import json
import os


def analyze_video(video_path):
    """
    Advanced Video OSINT using ffprobe
    - Extracts ALL available video metadata
    - Detects device, software & timeline leaks
    - Generates explainable exposure risk
    """

    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        data = json.loads(result.stdout)

        format_info = data.get("format", {})
        streams = data.get("streams", [])

        video_stream = next(
            (s for s in streams if s.get("codec_type") == "video"),
            {}
        )

        tags = format_info.get("tags", {}) or {}

        # ================= FULL METADATA =================
        metadata = {
            "File Name": os.path.basename(video_path),
            "File Size (MB)": round(int(format_info.get("size", 0)) / (1024 * 1024), 2),
            "Duration (seconds)": round(float(format_info.get("duration", 0)), 2),
            "Container Format": format_info.get("format_name"),
            "Overall Bitrate": format_info.get("bit_rate"),

            # Video stream details
            "Video Codec": video_stream.get("codec_name"),
            "Codec Description": video_stream.get("codec_long_name"),
            "Resolution": (
                f"{video_stream.get('width')}x{video_stream.get('height')}"
                if video_stream.get("width") else None
            ),
            "Frame Rate": video_stream.get("r_frame_rate"),
            "Pixel Format": video_stream.get("pix_fmt"),
            "Bit Depth": video_stream.get("bits_per_raw_sample"),

            # Embedded tags (identity leaks)
            "Creation Time": tags.get("creation_time"),
            "Encoder": tags.get("encoder"),
            "Recording Software": tags.get("software"),
            "Title": tags.get("title"),
            "Artist": tags.get("artist"),
            "Location": tags.get("location"),
        }

        # ================= RISK ANALYSIS =================
        risk = 0
        signals = []

        # Timestamp leakage
        if metadata.get("Creation Time"):
            risk += 6
            signals.append("Video metadata reveals creation timestamp")

        # Device / software fingerprint
        if metadata.get("Encoder") or metadata.get("Recording Software"):
            risk += 6
            signals.append("Video metadata reveals recording device or software")

        # Identity-linked tags
        for field in ["Title", "Artist", "Location"]:
            if metadata.get(field):
                risk += 4
                signals.append(f"Video metadata reveals {field.lower()} information")

        # Technical fingerprinting
        if metadata.get("Resolution"):
            risk += 3
            signals.append("Video resolution provides device fingerprint")

        if metadata.get("Frame Rate"):
            risk += 2
            signals.append("Video frame rate provides technical fingerprint")

        # Cap risk (video is high signal but not dominant)
        risk = min(risk, 30)

        return {
            "risk": risk,
            "signals": signals,
            "metadata": {k: v for k, v in metadata.items() if v},
            "evidence": (
                "Video OSINT analysis extracted embedded metadata, "
                "device fingerprints, timeline indicators, and identity-linked tags."
            )
        }

    except Exception:
        return {
            "risk": 0,
            "signals": [],
            "metadata": {},
            "evidence": "Video uploaded, but metadata extraction failed"
        }