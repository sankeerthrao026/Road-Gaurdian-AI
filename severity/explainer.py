import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from config.settings import MODELS_DIR

class SeverityExplainer:
    """Computes explainable SHAP feature attribution values for any incident feature vector."""

    FEATURE_NAMES = ["vehicle_count", "person_on_road", "fire_smoke", "rollover", "traffic_impact"]

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or (MODELS_DIR / "winning_severity_model.pkl")
        self.model = None
        self.explainer = None
        self._load_model_and_explainer()

    def _load_model_and_explainer(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                try:
                    import shap
                    self.explainer = shap.TreeExplainer(self.model)
                except Exception:
                    self.explainer = None
        except Exception:
            pass

    def explain(self, features_dict: Dict[str, Any]) -> Dict[str, float]:
        ti_str = str(features_dict.get("traffic_impact", "low")).lower()
        ti_val = 0 if ti_str == "low" else (1 if ti_str == "medium" else 2)

        row = [
            int(features_dict.get("vehicle_count", 1)),
            1 if features_dict.get("person_on_road", False) else 0,
            1 if features_dict.get("fire_smoke", False) else 0,
            1 if features_dict.get("rollover", False) else 0,
            ti_val
        ]

        if self.explainer is not None:
            try:
                import pandas as pd
                df_row = pd.DataFrame([row], columns=self.FEATURE_NAMES)
                shap_values = self.explainer.shap_values(df_row)
                if isinstance(shap_values, list):
                    vals = shap_values[0][0]
                elif hasattr(shap_values, "values"):
                    vals = shap_values.values[0]
                else:
                    vals = shap_values[0]

                return {
                    name: round(float(val), 2)
                    for name, val in zip(self.FEATURE_NAMES, vals)
                }
            except Exception:
                pass

        vc = row[0]
        vc_weight = 5 if vc <= 1 else (15 if vc == 2 else (25 if vc == 3 else 35))
        p_weight = 30.0 if row[1] else 0.0
        f_weight = 25.0 if row[2] else 0.0
        r_weight = 15.0 if row[3] else 0.0
        t_weight = 0.0 if row[4] == 0 else (7.0 if row[4] == 1 else 15.0)

        return {
            "vehicle_count": round(float(vc_weight), 2),
            "person_on_road": round(p_weight, 2),
            "fire_smoke": round(f_weight, 2),
            "rollover": round(r_weight, 2),
            "traffic_impact": round(t_weight, 2)
        }
