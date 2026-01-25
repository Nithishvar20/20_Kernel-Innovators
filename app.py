from osint.ai_image_detector import analyze_ai_image

from flask import Flask, render_template, request, send_file
from datetime import datetime
import os
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from osint.username_scan import scan_username
from osint.image_osint import extract_image_metadata
from osint.risk_engine import calculate_risk
from osint.history import save_scan, compare_last_scan
from osint.reverse_osint import detect_trackers
from osint.text_osint import analyze_text
from osint.geo_osint import infer_location
from osint.web_exposure import analyze_website_exposure
from osint.username_discovery import discover_username
from osint.username_enumerator import enumerate_username

# OPTIONAL MEDIA OSINT
try:
    from osint.video_osint import analyze_video
except Exception:
    analyze_video = None

try:
    from osint.audio_osint import analyze_audio
except Exception:
    analyze_audio = None


app = Flask(__name__)

LAST_SCAN = {}

# ================= ROUTES =================

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/scan", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return run_scan()
    return render_template("index.html")


# ================= AI IMAGE =================

@app.route("/ai-image-detector")
def ai_image_detector():
    return render_template("ai_image_detector.html")


@app.route("/ai-image-upload", methods=["POST"])
def ai_image_upload():
    image = request.files.get("image")

    if not image or image.filename == "":
        return "No image selected", 400

    os.makedirs("uploads", exist_ok=True)
    image_path = os.path.join("uploads", image.filename)
    image.save(image_path)

    ai_result = analyze_ai_image(image_path)

    return render_template(
        "ai_image_result.html",
        filename=image.filename,
        result=ai_result
    )
@app.route("/web-exposure")
def web_exposure():
    return render_template("web_exposure.html")


@app.route("/web-exposure/scan", methods=["POST"])
def web_exposure_scan():
    target = request.form.get("target")

    if not target:
        return render_template(
            "web_exposure.html",
            error="Please enter a domain or URL"
        )

    result = analyze_website_exposure(target)

    return render_template(
        "web_exposure_result.html",
        result=result
    )
@app.route("/username-exposure", methods=["GET", "POST"])
def username_exposure():
    result = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if username:
            result = discover_username(username)

    return render_template("username_exposure.html", result=result)

@app.route("/username-osint", methods=["GET", "POST"])
def username_osint():
    if request.method == "POST":
        username = request.form.get("username")

        if not username:
            return render_template(
                "username_scan.html",
                error="Username is required"
            )

        results = enumerate_username(username)

        return render_template(
            "username_result.html",
            username=username,
            results=results
        )

    return render_template("username_scan.html")

# ================= SCAN LOGIC =================

def run_scan():
    global LAST_SCAN

    platforms_found = {}
    inconclusive = set()

    image_data = None
    video_risk = {}
    audio_risk = {}
    text_risk = {}
    geo_risk = {}

    trackers = []
    mode = request.form.get("mode", "single")

    os.makedirs("uploads", exist_ok=True)

    # -------- MEDIA --------
    image_file = request.files.get("image_file")
    video_file = request.files.get("video_file")
    audio_file = request.files.get("audio_file")

    if image_file and image_file.filename:
        path = os.path.join("uploads", image_file.filename)
        image_file.save(path)
        image_data = extract_image_metadata(path)

    if video_file and video_file.filename and analyze_video:
        path = os.path.join("uploads", video_file.filename)
        video_file.save(path)
        video_risk = analyze_video(path)

    if audio_file and audio_file.filename and analyze_audio:
        path = os.path.join("uploads", audio_file.filename)
        audio_file.save(path)
        audio_risk = analyze_audio(path)

    # -------- USERNAME --------
    
    if mode == "single":
        username = request.form.get("single_username")
        if username:
            res = scan_username(username)
            platforms_found = res.get("platforms_found", {})
            inconclusive.update(res.get("inconclusive_platforms", []))

    else:
        platform_map = {
            "Instagram": request.form.get("instagram"),
            "Facebook": request.form.get("facebook"),
            "Threads": request.form.get("threads"),
        }

        for platform, uname in platform_map.items():
            if not uname:
                continue
    
            res = scan_username(uname, platform=platform)

            pf = res.get("platforms_found", {})
            if platform in pf:
                platforms_found[platform] = pf[platform]
            else:
                inconclusive.add(platform)

    # -------- TEXT --------
    text_input = request.form.get("text_input", "")
    if text_input.strip():
        text_risk = analyze_text(text_input)

    # -------- GEO --------
    if image_data:
        geo_risk = infer_location(image_data)

    correlated = {
        "platforms_found": platforms_found,
        "inconclusive_platforms": sorted(inconclusive),
        "text_risk": text_risk,
        "geo_risk": geo_risk,
        "image_metadata": image_data,
        "video_risk": video_risk,
        "audio_risk": audio_risk
    }

    risk = calculate_risk(correlated)

    try:
        compare_last_scan(correlated)
        save_scan(correlated)
    except Exception:
        pass

    for info in platforms_found.values():
        if isinstance(info, dict) and info.get("url"):
            trackers.extend(detect_trackers(info["url"]))

    LAST_SCAN = {
        "data": correlated,
        "risk": risk,
        "scan_time": datetime.now().strftime("%d %b %Y, %H:%M:%S")
    }

    return render_template(
        "result.html",
        data=correlated,
        risk=risk,
        trackers=set(trackers),
        scan_time=LAST_SCAN["scan_time"]
    )

# ================= SAFE PDF DOWNLOAD =================

@app.route("/download/pdf")
def download_pdf():
    if not LAST_SCAN:
        return "No scan data available", 400

    file_path = f"osint_report_{int(time.time())}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    margin_x = 50
    y = height - 60
    min_y = 60

    def new_page():
        nonlocal y
        c.showPage()
        y = height - 60

    def write(text, bold=False, size=11, indent=0):
        nonlocal y
        if y < min_y:
            new_page()
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(margin_x + indent, y, str(text))
        y -= size + 6

    def write_link(url, indent=0):
        nonlocal y
        if not url or not url.startswith("http"):
            return
        if y < min_y:
            new_page()
        c.setFont("Helvetica", 11)
        c.setFillColorRGB(0.1, 0.3, 0.8)
        c.drawString(margin_x + indent, y, url)
        w = c.stringWidth(url, "Helvetica", 11)
        c.linkURL(url, (margin_x + indent, y, margin_x + indent + w, y + 12))
        c.setFillColorRGB(0, 0, 0)
        y -= 18

    data = LAST_SCAN["data"]
    risk = LAST_SCAN["risk"]

    # ================= TITLE =================
    write("Exposure Intelligence Report", bold=True, size=18)
    write(f"Scan Time: {LAST_SCAN['scan_time']}")
    y -= 10

    # ================= PLATFORMS =================
    write("Platforms Identified", bold=True, size=14)
    for p, info in data.get("platforms_found", {}).items():
        write(p, bold=True, indent=10)
        if isinstance(info, dict):
            write_link(info.get("url"), indent=20)

    if data.get("inconclusive_platforms"):
        y -= 6
        write("Inconclusive Platforms", bold=True, indent=10)
        for p in data["inconclusive_platforms"]:
            write(f"- {p}", indent=20)

    y -= 10

    # ================= RISK SUMMARY =================
    write("Overall Risk Assessment", bold=True, size=14)
    write(f"Risk Score: {risk.get('score')} / 100", indent=10)
    write(f"Risk Level: {risk.get('level')}", indent=10)
    y -= 10

    # ================= IMAGE METADATA =================
    if data.get("image_metadata"):
        write("Image Metadata & OSINT", bold=True, size=14)
        for k, v in data["image_metadata"].items():
            write(f"{k}: {v}", indent=10)
        y -= 10

    # ================= VIDEO ANALYSIS =================
    if data.get("video_risk"):
        write("Video Metadata & Fingerprinting", bold=True, size=14)
        for k, v in data["video_risk"].items():
            if isinstance(v, list):
                write(f"{k}:", bold=True, indent=10)
                for item in v:
                    write(f"- {item}", indent=20)
            else:
                write(f"{k}: {v}", indent=10)
        y -= 10

    # ================= AUDIO ANALYSIS =================
    if data.get("audio_risk"):
        write("Audio Metadata & OSINT", bold=True, size=14)
        for k, v in data["audio_risk"].items():
            write(f"{k}: {v}", indent=10)
        y -= 10

    # ================= TEXT OSINT =================
    if data.get("text_risk"):
        write("Text OSINT & Content Signals", bold=True, size=14)
        for k, v in data["text_risk"].items():
            write(f"{k}: {v}", indent=10)
        y -= 10

    # ================= GEO INFERENCE =================
    if data.get("geo_risk"):
        write("Geolocation Inference", bold=True, size=14)
        for k, v in data["geo_risk"].items():
            write(f"{k}: {v}", indent=10)
        y -= 10

    c.save()
    return send_file(file_path, as_attachment=True)

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)
