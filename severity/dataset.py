import numpy as np
import pandas as pd

def calculate_rule_score(vehicle_count: int, person_on_road: int, fire_smoke: int, rollover: int, traffic_impact_val: int) -> int:
    if vehicle_count <= 1:
        v_weight = 5
    elif vehicle_count == 2:
        v_weight = 15
    elif vehicle_count == 3:
        v_weight = 25
    else:
        v_weight = 35

    t_weight = 0 if traffic_impact_val == 0 else (7 if traffic_impact_val == 1 else 15)

    raw_score = (
        v_weight
        + (30 if person_on_road else 0)
        + (25 if fire_smoke else 0)
        + (15 if rollover else 0)
        + t_weight
    )
    return int(np.clip(raw_score, 0, 100))

def score_to_label(score: float) -> str:
    if score < 30:
        return "Low"
    elif score < 55:
        return "Medium"
    elif score < 80:
        return "High"
    else:
        return "Critical"

def generate_synthetic_dataset(n_samples: int = 800, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)

    vehicle_count = np.random.choice([1, 2, 3, 4, 5, 6], size=n_samples, p=[0.35, 0.30, 0.20, 0.08, 0.05, 0.02])
    person_on_road = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
    fire_smoke = np.random.choice([0, 1], size=n_samples, p=[0.82, 0.18])
    rollover = np.random.choice([0, 1], size=n_samples, p=[0.90, 0.10])

    traffic_impact = []
    for vc in vehicle_count:
        if vc < 2:
            ti = np.random.choice([0, 1], p=[0.8, 0.2])
        elif vc <= 4:
            ti = np.random.choice([0, 1, 2], p=[0.15, 0.70, 0.15])
        else:
            ti = np.random.choice([1, 2], p=[0.25, 0.75])
        traffic_impact.append(ti)
    traffic_impact = np.array(traffic_impact)

    base_scores = [
        calculate_rule_score(vc, p, f, r, t)
        for vc, p, f, r, t in zip(vehicle_count, person_on_road, fire_smoke, rollover, traffic_impact)
    ]

    noise = np.random.normal(0, 2.5, size=n_samples)
    scores = np.clip(np.round(np.array(base_scores) + noise), 0, 100).astype(int)
    labels = [score_to_label(s) for s in scores]

    df = pd.DataFrame({
        "vehicle_count": vehicle_count,
        "person_on_road": person_on_road,
        "fire_smoke": fire_smoke,
        "rollover": rollover,
        "traffic_impact": traffic_impact,
        "severity_score": scores,
        "severity_label": labels
    })

    return df
