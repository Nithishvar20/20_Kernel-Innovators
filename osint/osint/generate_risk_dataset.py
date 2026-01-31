import csv
import random
import os

OUTPUT_FILE = "osint/data/risk_dataset.csv"
TOTAL_PER_CLASS = 333

os.makedirs("osint/data", exist_ok=True)

header = [
    "platform_count",
    "high_confidence_accounts",
    "private_profiles",
    "image_metadata",
    "media_risk",
    "text_risk",
    "identity_correlation",
    "label"
]

rows = []

def gen_low():
    return [
        random.randint(1, 2),
        random.randint(0, 1),
        random.randint(0, 1),
        0,
        random.randint(0, 5),
        random.randint(0, 5),
        random.choice([0, 5, 10]),
        "LOW"
    ]

def gen_medium():
    return [
        random.randint(3, 4),
        random.randint(2, 3),
        random.randint(0, 1),
        random.choice([0, 1]),
        random.randint(10, 30),
        random.randint(5, 15),
        random.choice([10, 20, 30]),
        "MEDIUM"
    ]

def gen_high():
    return [
        random.randint(5, 10),
        random.randint(4, 9),
        0,
        1,
        random.randint(30, 90),
        random.randint(20, 70),
        random.randint(30, 90),
        "HIGH"
    ]

for _ in range(TOTAL_PER_CLASS):
    rows.append(gen_low())
    rows.append(gen_medium())
    rows.append(gen_high())

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)   # ✅ HEADER GUARANTEED
    writer.writerows(rows)

print(f"[✔] Generated {len(rows)} samples with header at {OUTPUT_FILE}")