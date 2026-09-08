"""
Train Kick & Well-Control Anomaly ML Risk Model.
"""
from pathlib import Path
import sys
from sklearn.model_selection import train_test_split
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.ml.feature_engineering import FEATURE_COLUMNS
from scripts.train_models import build_training_dataset, train_and_evaluate_model, MODELS_DIR

def main():
    print("[INFO] Building features and training Kick / Well Control Random Forest Risk Model...")
    df = build_training_dataset()
    X = df[FEATURE_COLUMNS]
    y = df["target_kick"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model, metrics = train_and_evaluate_model(X_train, X_test, y_train, y_test, "Kick / Well Control Model", "KICK")
    model_path = MODELS_DIR / "kick_model.joblib"
    joblib.dump(model, model_path)
    print(f"[SUCCESS] Saved model to {model_path}")

if __name__ == "__main__":
    main()
