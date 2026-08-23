import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, f1_score, confusion_matrix
from config.settings import MODELS_DIR, MLRUNS_DIR, MLFLOW_EXPERIMENT_NAME
from severity.dataset import generate_synthetic_dataset, score_to_label

def train_and_evaluate_models():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_dataset(n_samples=800, seed=42)

    features = ["vehicle_count", "person_on_road", "fire_smoke", "rollover", "traffic_impact"]
    X = df[features]
    y = df["severity_score"]
    y_labels = df["severity_label"]

    X_train, X_test, y_train, y_test, label_train, label_test = train_test_split(
        X, y, y_labels, test_size=0.25, random_state=42
    )

    models_to_train = {
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
    }

    try:
        import xgboost as xgb
        models_to_train["XGBoost"] = xgb.XGBRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42
        )
    except Exception:
        models_to_train["XGBoost"] = GradientBoostingRegressor(
            n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42
        )

    mlflow_active = False
    try:
        import mlflow
        import mlflow.sklearn
        mlflow.set_tracking_uri(f"file:///{MLRUNS_DIR}")
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
        mlflow_active = True
    except Exception as e:
        print(f"[MLflow] Offline / local tracking mode: {e}")

    results = {}
    best_model_name = None
    best_r2 = -float("inf")
    best_model = None

    class_names = ["Low", "Medium", "High", "Critical"]

    for name, model in models_to_train.items():
        print(f"\n--- Training {name} ---")
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        preds_clipped = np.clip(preds, 0, 100)
        pred_labels = [score_to_label(p) for p in preds_clipped]

        rmse = float(np.sqrt(mean_squared_error(y_test, preds_clipped)))
        mae = float(mean_absolute_error(y_test, preds_clipped))
        r2 = float(r2_score(y_test, preds_clipped))
        acc = float(accuracy_score(label_test, pred_labels))
        f1 = float(f1_score(label_test, pred_labels, average="weighted"))
        cm = confusion_matrix(label_test, pred_labels, labels=class_names).tolist()

        model_metrics = {
            "model_name": name,
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "r2_score": round(r2, 4),
            "accuracy": round(acc, 4),
            "f1_weighted": round(f1, 4),
            "confusion_matrix": cm,
            "classes": class_names,
            "n_train": len(X_train),
            "n_test": len(X_test),
        }
        results[name] = model_metrics
        print(f"[{name}] RMSE: {rmse:.3f}, MAE: {mae:.3f}, R2: {r2:.4f}, Accuracy: {acc*100:.2f}%, F1: {f1:.4f}")

        if mlflow_active:
            try:
                import mlflow
                with mlflow.start_run(run_name=f"{name}_Run"):
                    mlflow.log_param("model_type", name)
                    mlflow.log_param("n_samples", len(df))
                    mlflow.log_metric("rmse", rmse)
                    mlflow.log_metric("mae", mae)
                    mlflow.log_metric("r2_score", r2)
                    mlflow.log_metric("accuracy", acc)
                    mlflow.log_metric("f1_weighted", f1)
                    mlflow.sklearn.log_model(model, artifact_path=name.lower())
            except Exception as ex:
                pass

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model = model

    winning_info = {
        "winner": best_model_name,
        "selection_rationale": f"{best_model_name} demonstrated superior generalization with R² of {results[best_model_name]['r2_score']} and F1 score of {results[best_model_name]['f1_weighted']}.",
        "models": results
    }

    joblib.dump(best_model, MODELS_DIR / "winning_severity_model.pkl")
    joblib.dump(models_to_train.get("RandomForest"), MODELS_DIR / "rf_model.pkl")
    joblib.dump(models_to_train.get("XGBoost"), MODELS_DIR / "xgb_model.pkl")

    with open(MODELS_DIR / "model_comparison.json", "w") as f:
        json.dump(winning_info, f, indent=2)

    print(f"\n>> Selected Winner: {best_model_name} (Saved to {MODELS_DIR / 'winning_severity_model.pkl'})")
    return winning_info

if __name__ == "__main__":
    train_and_evaluate_models()
