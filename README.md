# Exposure Intelligence

Exposure Intelligence is a modular **OSINT (Open-Source Intelligence)** platform designed to analyze digital exposure, identity linkage, and **AI-manipulated media**.  
The project focuses on **face-level verification**, cross-signal risk correlation, and evidence-ready reporting.

---

## Features

### OSINT & Exposure Analysis
- Username footprint scanning across multiple platforms
- Reverse image OSINT (image reuse, exposure, engagement signals)
- Website exposure and metadata analysis
- Text-based and geolocation risk inference

### AI & Synthetic Media Detection
- **AI Image Detection**  
  Identifies AI-generated or manipulated images

- **AI Face Morph Detection (Prototype)**  
  - Performs **face-level analysis** on group images  
  - Distinguishes **AI-morphed faces vs authentic faces**  
  - Visual bounding boxes with confidence scores  
  - Designed for investigative triage and demonstrations  

### Risk & Reporting
- Correlation-based risk engine
- Confidence scoring
- PDF report generation for documentation and review

---

## AI Face Morph Detection (Prototype)

**Problem:**  
Image-level AI detection fails when only some faces in a group image are manipulated.

**Solution:**  
This module analyzes each detected face independently, allowing identification of:
- AI-morphed individuals
- Authentic individuals
- Visual attribution with confidence scoring

> Note: This feature is a **prototype** intended for awareness, triage, and demonstration purposes.  
> It is not designed for forensic or legal certainty.

---

## Project Structure
