"""
NWIS ML Evaluation Module.
Inspects saved models, prints metrics, confusion matrix summaries, and feature importances.
"""
import json
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent.parent
METRICS_PATH = BASE_DIR / "artifacts" / "evaluation" / "model_metrics.json"

def display_evaluation_summary():
    if not METRICS_PATH.exists():
        print(f"[ERROR] Metrics file not found at {METRICS_PATH}. Run training first.")
        return

    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)

    print("=" * 60)
    print(" NWIS ML RISK PREDICTION MODELS - EVALUATION SUMMARY")
    print("=" * 60)
    for model_name, data in metrics.items():
        print(f"\nModel: {model_name.upper()}")
        print(f"  Accuracy:  {data.get('accuracy', 0.0):.4f}")
        print(f"  Precision: {data.get('precision', 0.0):.4f}")
        print(f"  Recall:    {data.get('recall', 0.0):.4f}")
        print(f"  F1 Score:  {data.get('f1', 0.0):.4f}")
        print(f"  ROC-AUC:   {data.get('roc_auc', 0.0):.4f}")
        print("  Top Contributing Feature Importances:")
        for feat, imp in list(data.get("feature_importances", {}).items())[:5]:
            print(f"    - {feat:25s}: {imp:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    display_evaluation_summary()
