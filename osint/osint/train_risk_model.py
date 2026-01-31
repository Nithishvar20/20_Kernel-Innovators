import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

DATA_PATH = "osint/data/risk_dataset.csv"
MODEL_PATH = "osint/models/risk_model.pkl"
ENCODER_PATH = "osint/models/label_encoder.pkl"
FEATURES_PATH = "osint/models/feature_columns.pkl"

df = pd.read_csv(DATA_PATH)

print("[DEBUG] Columns:", df.columns.tolist())

FEATURE_COLS = [
    "platform_count",
    "high_confidence_accounts",
    "private_profiles",
    "image_metadata",
    "media_risk",
    "text_risk",
    "identity_correlation"
]

X = df[FEATURE_COLS]
y = df["label"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)

joblib.dump(model, MODEL_PATH)
joblib.dump(le, ENCODER_PATH)
joblib.dump(FEATURE_COLS, FEATURES_PATH)

print("[✔] Risk model trained successfully")