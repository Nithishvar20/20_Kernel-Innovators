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

# ----------------- STORE LAST SCAN (FOR PDF) -----------------
LAST_SCAN = {}


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/scan", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return run_scan()
    return render_template("index.html")


# ================= SCAN LOGIC =================
def run_scan():

    global LAST_SCAN

    # ---- PRE-INITIALIZE VARIABLES ----
    platforms_found = {}
    inconclusive = set()

    image_data = None
    video_risk = {}
    audio_risk = {}

    text_risk = {}
    geo_risk = {}

    risk = 0
    new_findings = []
    trackers = []

    mode = request.form.get("mode", "single")

    # ================= MEDIA (FIXED, PARALLEL) =================
    image_file = request.files.get("image_file")
    video_file = request.files.get("video_file")
    audio_file = request.files.get("audio_file")

    os.makedirs("uploads", exist_ok=True)

    # ---------- IMAGE ----------
    if image_file and image_file.filename:
        img_path = os.path.join("uploads", image_file.filename)
        image_file.save(img_path)
        try:
            image_data = extract_image_metadata(img_path)
        except Exception as e:
            print("Image OSINT error:", e)

    # ---------- VIDEO ----------
    if video_file and video_file.filename and analyze_video:
        vid_path = os.path.join("uploads", video_file.filename)
        video_file.save(vid_path)
        try:
            video_risk = analyze_video(vid_path)
        except Exception as e:
            print("Video OSINT error:", e)

    # ---------- AUDIO ----------
    if audio_file and audio_file.filename and analyze_audio:
        aud_path = os.path.join("uploads", audio_file.filename)
        audio_file.save(aud_path)
        try:
            audio_risk = analyze_audio(aud_path)
        except Exception as e:
            print("Audio OSINT error:", e)

    # ================= USERNAME =================
    if mode == "single":
        username = request.form.get("single_username")
        if username:
            res = scan_username(username)
            platforms_found = res.get("platforms_found", {})
            inconclusive.update(res.get("inconclusive_platforms", []))
    else:
        platforms = {
            "Instagram": request.form.get("instagram"),
            "GitHub": request.form.get("github"),
            "Facebook": request.form.get("facebook"),
            "Threads": request.form.get("threads"),
            "Reddit": request.form.get("reddit"),
            "LinkedIn": request.form.get("linkedin"),
        }

        for platform, uname in platforms.items():
            if not uname:
                continue
            res = scan_username(uname)
            pf = res.get("platforms_found", {})
            if platform in pf:
                platforms_found[platform] = pf[platform]
            inconclusive.update(res.get("inconclusive_platforms", []))

    # ================= TEXT =================
    text_input = request.form.get("text_input", "")
    text_risk = analyze_text(text_input) if text_input.strip() else {}

    # ================= GEO =================
    geo_risk = infer_location(image_data) if image_data else {}

    # ================= FINAL DATA =================
    correlated = {
        "platforms_found": platforms_found,
        "inconclusive_platforms": sorted(inconclusive),
        "text_risk": text_risk,
        "geo_risk": geo_risk,
        "image_metadata": image_data,
        "video_risk": video_risk,
        "audio_risk": audio_risk
    }

    # ================= RISK =================
    risk = calculate_risk(correlated)

    # ================= HISTORY =================
    try:
        new_findings = compare_last_scan(correlated)
        save_scan(correlated)
    except Exception:
        new_findings = []

    # ================= TRACKERS =================
    for info in platforms_found.values():
        if isinstance(info, dict) and info.get("url"):
            try:
                trackers.extend(detect_trackers(info["url"]))
            except Exception:
                pass

    # ================= SAVE FOR PDF =================
    LAST_SCAN = {
        "data": correlated,
        "risk": risk,
        "scan_time": datetime.now().strftime("%d %b %Y, %H:%M:%S")
    }

    # ================= RESULT =================
    return render_template(
        "result.html",
        data=correlated,
        risk=risk,
        new_findings=new_findings,
        trackers=set(trackers),
        image_metadata=image_data,
        scan_time=LAST_SCAN["scan_time"]
    )


# ================= PDF DOWNLOAD =================
@app.route("/download/pdf")
def download_pdf():

    if not LAST_SCAN:
        return "No scan data available", 400

    file_path = f"osint_report_{int(time.time())}.pdf"
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    def new_page():
        c.showPage()
        draw_background()
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 11)
        return height - 60

    def draw_background():
        c.saveState()
        c.setFillColorRGB(0.97, 0.97, 0.98)  # premium light background
        c.rect(0, 0, width, height, stroke=0, fill=1)
        c.restoreState()

    draw_background()
    c.setFillColorRGB(0, 0, 0)

    margin_x = 50
    y = height - 60
    min_y = 60

    data = LAST_SCAN["data"]
    risk = LAST_SCAN["risk"]
    scan_time = LAST_SCAN["scan_time"]

    def write_line(text, bold=False, indent=0):
        nonlocal y
        if y < min_y:
            y = new_page()
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 11 if not bold else 14)
        c.drawString(margin_x + indent, y, text)
        y -= 16

    # ================= HEADER =================
    write_line("Exposure Intelligence Report", bold=True)
    write_line(f"Scan Time: {scan_time}")
    y -= 10
    c.line(margin_x, y, width - margin_x, y)
    y -= 20

    # ================= EXECUTIVE SUMMARY =================
    write_line("Executive Summary", bold=True)
    write_line(f"• Platforms Identified: {len(data['platforms_found'])}", indent=10)
    write_line(f"• Overall Risk Score: {risk['score']} / 100 ({risk['level']})", indent=10)
    y -= 10

    # ================= PLATFORMS =================
    if data["platforms_found"]:
        write_line("Identified Platforms", bold=True)
        for platform, info in data["platforms_found"].items():
            write_line(f"- {platform}: {info.get('url','')}", indent=10)
        y -= 10

    # ================= TEXT OSINT =================
    if data.get("text_risk"):
        write_line("Text OSINT Findings", bold=True)
        for k, v in data["text_risk"].items():
            write_line(f"- {k}: {v}", indent=10)
        y -= 10

    # ================= IMAGE OSINT =================
    if data.get("image_metadata"):
        write_line("Image Metadata OSINT", bold=True)
        for k, v in data["image_metadata"].items():
            if k != "gps":
                write_line(f"- {k}: {v}", indent=10)

        if "gps" in data["image_metadata"]:
            gps = data["image_metadata"]["gps"]
            write_line(f"- GPS Location: Lat {gps['lat']}, Lon {gps['lon']}", indent=10)
        y -= 10

    # ================= VIDEO OSINT =================
    if data.get("video_risk") and data["video_risk"]:
        write_line("Video OSINT Metadata", bold=True)
        for k, v in data["video_risk"].get("metadata", {}).items():
            write_line(f"- {k}: {v}", indent=10)
        y -= 10

    # ================= AUDIO OSINT =================
    if data.get("audio_risk") and data["audio_risk"]:
        write_line("Audio OSINT Metadata", bold=True)
        for k, v in data["audio_risk"].get("metadata", {}).items():
            write_line(f"- {k}: {v}", indent=10)
        y -= 10

    # ================= RISK FACTORS =================
    if risk.get("reasons"):
        write_line("Key Risk Factors", bold=True)
        for r in risk["reasons"]:
            write_line(f"- {r}", indent=10)

    # ================= DISCLAIMER =================
    y -= 20
    if y < min_y:
        y = new_page()

    c.setFont("Helvetica", 9)
    c.drawString(
        margin_x, y,
        "This report is generated using ethical Open Source Intelligence (OSINT) only."
    )
    y -= 12
    c.drawString(
        margin_x, y,
        "No private, paid, or restricted data sources were accessed. Results indicate potential exposure, not certainty."
    )

    c.showPage()
    c.save()

    return send_file(file_path, as_attachment=True)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)