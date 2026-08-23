from typing import Dict, Any, List
from datetime import datetime

class ResponseAgent:
    """
    Determines emergency and operational workflows based on incident severity and type.
    Clearly outputs timestamped notification objects labeled SIMULATED NOTIFICATION.
    """

    @staticmethod
    def plan_response(incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        severity = incident.get("severity_label", "Low")
        score = incident.get("severity_score", 0)
        inc_type = incident.get("type", "unknown").lower()
        features = incident.get("features", {})
        cam_id = incident.get("camera_id", "CAM-01")
        loc_name = incident.get("location", {}).get("name", "Highway Corridor")
        inc_id = incident.get("incident_id", "UNKNOWN")

        actions = []
        now_iso = datetime.now().isoformat()

        # Critical / High Collisions & Fires -> Hospital & Highway Police
        if severity in ["Critical", "High"] or score >= 55 or features.get("fire_smoke") or features.get("person_on_road"):
            actions.append({
                "service": "Emergency Medical Services (EMS) / Trauma Center",
                "status": "DISPATCH_TRIGGERED",
                "priority": "P1 - IMMEDIATE",
                "units": 2 if features.get("person_on_road") else 1,
                "message": f"High-velocity impact incident detected at {loc_name}. Medical triage team en route.",
                "badge": "SIMULATED EMERGENCY NOTIFICATION SENT",
                "timestamp": now_iso,
                "target_incident": inc_id
            })
            actions.append({
                "service": "Highway Patrol & Traffic Enforcement",
                "status": "DISPATCH_TRIGGERED",
                "priority": "P1 - LANE CLOSURE",
                "units": 2,
                "message": f"Block and divert traffic approaching {loc_name} ({cam_id}). Collision scene control.",
                "badge": "SIMULATED NOTIFICATION SENT",
                "timestamp": now_iso,
                "target_incident": inc_id
            })
            if features.get("fire_smoke") or inc_type == "fire":
                actions.append({
                    "service": "Fire & Rescue Department",
                    "status": "DISPATCH_TRIGGERED",
                    "priority": "P1 - RAPID RESPONSE",
                    "units": 1,
                    "message": f"Highway vehicle fire detected at {loc_name}. Chemical suppression unit deployed.",
                    "badge": "SIMULATED NOTIFICATION SENT",
                    "timestamp": now_iso,
                    "target_incident": inc_id
                })

        # Medium Severity Collision
        elif severity == "Medium" or score >= 30:
            actions.append({
                "service": "Highway Patrol & Traffic Enforcement",
                "status": "PATROL_DISPATCHED",
                "priority": "P2 - TRAFFIC CONTROL",
                "units": 1,
                "message": f"Moderate collision incident reported at {loc_name}. Patrol unit assigned for clearance.",
                "badge": "SIMULATED NOTIFICATION SENT",
                "timestamp": now_iso,
                "target_incident": inc_id
            })
            actions.append({
                "service": "Roadside Assistance & Towing",
                "status": "DISPATCH_TRIGGERED",
                "priority": "P2 - VEHICLE RECOVERY",
                "units": 1,
                "message": f"Towing and recovery vehicle assigned to {loc_name}.",
                "badge": "SIMULATED REQUEST SENT",
                "timestamp": now_iso,
                "target_incident": inc_id
            })

        # Low Severity / Incident Monitoring
        else:
            actions.append({
                "service": "Traffic Operations Center",
                "status": "MONITORING_ACTIVE",
                "priority": "P3 - LOW",
                "units": 0,
                "message": f"Minor road incident observed at {loc_name}. Automated CCTV tracking active.",
                "badge": "SIMULATED NOTIFICATION SENT",
                "timestamp": now_iso,
                "target_incident": inc_id
            })

        return actions
