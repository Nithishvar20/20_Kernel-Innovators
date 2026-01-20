import subprocess
import json
import os


def analyze_audio(audio_path):
    """
    Advanced Audio OSINT using ffprobe
    - Extracts ALL available metadata
    - Identifies exposure signals
    - Generates explainable risk score
    """

    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            audio_path
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

        audio_stream = next(
            (s for s in streams if s.get("codec_type") == "audio"),
            {}
        )

        tags = format_info.get("tags", {}) or {}

        # ================= METADATA (FULL) =================
        metadata = {
            "File Name": os.path.basename(audio_path),
            "File Size (MB)": round(int(format_info.get("size", 0)) / (1024 * 1024), 2),
            "Duration (seconds)": round(float(format_info.get("duration", 0)), 2),
            "Container Format": format_info.get("format_name"),
            "Overall Bitrate": format_info.get("bit_rate"),

            # Audio stream details
            "Audio Codec": audio_stream.get("codec_name"),
            "Codec Description": audio_stream.get("codec_long_name"),
            "Sample Rate (Hz)": audio_stream.get("sample_rate"),
            "Channels": audio_stream.get("channels"),
            "Channel Layout": audio_stream.get("channel_layout"),
            "Bits Per Sample": audio_stream.get("bits_per_sample"),

            # Embedded tags (identity leaks)
            "Title": tags.get("title"),
            "Artist": tags.get("artist"),
            "Album": tags.get("album"),
            "Author": tags.get("author"),
            "Creation Time": tags.get("creation_time"),
            "Encoder": tags.get("encoder"),
            "Recording Software": tags.get("software"),
        }

        # ================= RISK ANALYSIS =================
        risk = 0
        signals = []

        # Timestamp leakage
        if metadata.get("Creation Time"):
            risk += 6
            signals.append("Audio metadata reveals recording timestamp")

        # Device / software fingerprint
        if metadata.get("Encoder") or metadata.get("Recording Software"):
            risk += 6
            signals.append("Audio metadata reveals recording device or software")

        # Identity-linked tags
        for field in ["Artist", "Author", "Album", "Title"]:
            if metadata.get(field):
                risk += 4
                signals.append(f"Audio metadata reveals {field.lower()} information")

        # Technical fingerprinting
        if metadata.get("Sample Rate (Hz)"):
            risk += 3
            signals.append("Audio technical fingerprint detected")

        if metadata.get("Channels", 0) >= 2:
            risk += 2
            signals.append("Stereo audio suggests edited or high-quality recording")

        # Cap risk to stay proportional
        risk = min(risk, 25)

        return {
            "risk": risk,
            "signals": signals,
            "metadata": {k: v for k, v in metadata.items() if v},
            "evidence": (
                "Audio OSINT analysis extracted embedded metadata, "
                "technical fingerprints, and potential identity indicators."
            )
        }

    except Exception as e:
        return {
            "risk": 0,
            "signals": [],
            "metadata": {},
            "evidence": "Audio uploaded, but metadata extraction failed"
        }