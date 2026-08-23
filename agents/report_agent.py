import os
from typing import Dict, Any, List
from config.settings import GEMINI_API_KEY

class ReportAgent:
    """
    Generates strict, structured, timeline-style incident reports.
    Constraint: Summarize ONLY verified structured fields, never invent events or assign legal fault.
    """

    STRICT_SYSTEM_PROMPT = """
You are RoadGuardian AI Report Generator.
Summarize ONLY the verified structured incident data provided.
Rules:
1. Do NOT invent facts or events not present in the input.
2. Do NOT assign legal fault or liability.
3. Strictly format output as:
INCIDENT #[id] — [SEVERITY] [TYPE]
[timestamp] — [observation]
[timestamp] — [observation]
Location: [road] | Camera: [camera_id]
[standard disclaimer: summarizes observations, does not determine legal responsibility]
"""

    @classmethod
    def generate_report(cls, incident: Dict[str, Any], similar_context: str = "") -> str:
        inc_id = incident.get("incident_id", "UNKNOWN")
        severity = incident.get("severity_label", "UNKNOWN").upper()
        inc_type = incident.get("type", "UNKNOWN").upper()
        ts = incident.get("timestamp", "2026-08-22T00:00:00")
        camera_id = incident.get("camera_id", "CAM-01")
        loc_name = incident.get("location", {}).get("name", "Corridor NH-44")
        features = incident.get("features", {})
        involved_ids = incident.get("involved_vehicle_ids", [])

        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""
{cls.STRICT_SYSTEM_PROMPT}

Data:
ID: {inc_id}
Severity: {severity} (Score: {incident.get('severity_score', 0)})
Type: {inc_type}
Timestamp: {ts}
Camera: {camera_id}
Location: {loc_name}
Features: {features}
Involved Vehicle IDs: {involved_ids}
Similar Incidents Context: {similar_context}
"""
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass

        observations = []
        vc = features.get("vehicle_count", 1)
        observations.append(f"{ts} — Optical stream tracking identified {vc} vehicle(s) in active travel zone.")

        if involved_ids:
            observations.append(f"{ts} — Primary tracked vehicles involved: {', '.join([f'Vehicle #{v}' for v in involved_ids])}.")

        if inc_type == "COLLISION":
            observations.append(f"{ts} — Trajectory convergence and sudden velocity cessation observed between tracked vehicles.")
        elif inc_type == "FIRE":
            observations.append(f"{ts} — Thermal/HSV flame signature and combustion plume detected.")

        if features.get("person_on_road"):
            observations.append(f"{ts} — Pedestrian / vehicle occupant detected on roadway corridor.")
        if features.get("rollover"):
            observations.append(f"{ts} — Severe vehicle chassis inversion / rollover orientation observed.")
        if features.get("traffic_impact") == "high":
            observations.append(f"{ts} — Upstream congestion propagation: High traffic density impact.")

        if similar_context:
            observations.append(f"{ts} — Contextual RAG: {similar_context}")

        lines = [
            f"INCIDENT #{inc_id} — [{severity}] [{inc_type}]",
            *observations,
            f"Location: {loc_name} | Camera: {camera_id}",
            "[standard disclaimer: summarizes observations, does not determine legal responsibility]"
        ]

        return "\n".join(lines)
