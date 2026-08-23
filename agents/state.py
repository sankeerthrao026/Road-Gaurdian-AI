import threading
from typing import Dict, List, Any, Optional
from datetime import datetime

class IncidentStore:
    """Thread-safe state store for active incidents and camera tracking."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(IncidentStore, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.incidents: Dict[str, Dict[str, Any]] = {}
        self.active_order: List[str] = []
        self.camera_status: Dict[str, Dict[str, Any]] = {}
        self.dispatch_log: List[Dict[str, Any]] = []

    def upsert_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            inc_id = incident_data["incident_id"]
            if inc_id in self.incidents:
                existing = self.incidents[inc_id]
                existing.update(incident_data)
                if "timeline" not in existing:
                    existing["timeline"] = []
                existing["timeline"].append({
                    "timestamp": incident_data.get("timestamp", datetime.now().isoformat()),
                    "event": f"Updated: Severity {existing.get('severity_score', 0)} ({existing.get('severity_label', 'Unknown')})",
                    "features": incident_data.get("features", {})
                })
                self.incidents[inc_id] = existing
            else:
                incident_data["created_at"] = incident_data.get("timestamp", datetime.now().isoformat())
                incident_data["timeline"] = [{
                    "timestamp": incident_data.get("timestamp", datetime.now().isoformat()),
                    "event": f"Incident Detected: {incident_data.get('type', 'Unknown').upper()}",
                    "features": incident_data.get("features", {})
                }]
                self.incidents[inc_id] = incident_data

            self._recalculate_priorities()
            return self.incidents[inc_id]

    def _recalculate_priorities(self):
        sorted_keys = sorted(
            self.incidents.keys(),
            key=lambda k: (
                self.incidents[k].get("severity_score", 0),
                self.incidents[k].get("timestamp", "")
            ),
            reverse=True
        )
        self.active_order = sorted_keys
        for rank, inc_id in enumerate(self.active_order, start=1):
            self.incidents[inc_id]["priority_rank"] = rank

    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.incidents.get(incident_id)

    def get_all_active_sorted(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self.incidents[k] for k in self.active_order if k in self.incidents]

    def add_dispatch(self, dispatch_entry: Dict[str, Any]):
        with self._lock:
            self.dispatch_log.insert(0, dispatch_entry)
            if len(self.dispatch_log) > 50:
                self.dispatch_log.pop()

    def get_dispatches(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.dispatch_log)

    def clear(self):
        with self._lock:
            self.incidents.clear()
            self.active_order.clear()
            self.dispatch_log.clear()

global_incident_store = IncidentStore()
