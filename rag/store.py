import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from config.settings import CHROMA_DIR

class IncidentRAGStore:
    """Local ChromaDB / Semantic vector store for historical incident recall."""

    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir or CHROMA_DIR
        self.client = None
        self.collection = None
        self.fallback_documents: List[Dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = self.client.get_or_create_collection(
                name="road_incidents_history",
                metadata={"description": "Historical road incident reports and features"}
            )
            print("[IncidentRAGStore] ChromaDB persistent collection initialized.")
        except Exception as e:
            print(f"[IncidentRAGStore] ChromaDB offline mode ({e}). Utilizing in-memory semantic store.")
            self._load_seed_history()

    def _load_seed_history(self):
        self.fallback_documents = [
            {
                "id": "HIST_001",
                "text": "Severe high-speed multi-vehicle collision on NH-44 KM 122 involving 3 cars with pedestrian risk, high traffic blockage.",
                "metadata": {
                    "incident_id": "HIST_001",
                    "type": "collision",
                    "severity": "High",
                    "severity_score": 75,
                    "location": "NH-44 Corridor",
                    "timestamp": "2026-08-15T09:20:00"
                }
            },
            {
                "id": "HIST_002",
                "text": "Cargo truck fire on Outer Ring Road Flyover with heavy smoke plume and lane closure.",
                "metadata": {
                    "incident_id": "HIST_002",
                    "type": "fire",
                    "severity": "Critical",
                    "severity_score": 88,
                    "location": "Outer Ring Road Junction",
                    "timestamp": "2026-08-18T18:45:00"
                }
            },
            {
                "id": "HIST_003",
                "text": "Multi-car collision on Interstate junction causing traffic congestion and lane blockage.",
                "metadata": {
                    "incident_id": "HIST_003",
                    "type": "collision",
                    "severity": "Medium",
                    "severity_score": 45,
                    "location": "I-35W Corridor",
                    "timestamp": "2026-08-20T11:10:00"
                }
            }
        ]

    def add_incident(self, incident: Dict[str, Any]):
        inc_id = incident.get("incident_id", "TEMP_001")
        features = incident.get("features", {})
        report = incident.get("report_text", "")
        doc_text = f"Incident {inc_id}: Type {incident.get('type')}, Severity {incident.get('severity_label')} (Score: {incident.get('severity_score')}). Features: {features}. Report: {report}"

        metadata = {
            "incident_id": inc_id,
            "type": str(incident.get("type", "unknown")),
            "severity": str(incident.get("severity_label", "Low")),
            "severity_score": int(incident.get("severity_score", 0)),
            "location": str(incident.get("location", {}).get("name", "Corridor")),
            "timestamp": str(incident.get("timestamp", ""))
        }

        if self.collection is not None:
            try:
                self.collection.upsert(
                    ids=[inc_id],
                    documents=[doc_text],
                    metadatas=[metadata]
                )
                return
            except Exception:
                pass

        self.fallback_documents.append({"id": inc_id, "text": doc_text, "metadata": metadata})

    def find_similar_incidents(self, incident: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        query_text = f"Incident type {incident.get('type')} with severity {incident.get('severity_label')}, vehicles {incident.get('features', {}).get('vehicle_count')} at {incident.get('location', {}).get('name')}"

        if self.collection is not None:
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=min(top_k, max(1, self.collection.count()))
                )
                if results and results.get("metadatas") and len(results["metadatas"][0]) > 0:
                    matched = []
                    for i, meta in enumerate(results["metadatas"][0]):
                        doc = results["documents"][0][i] if "documents" in results else ""
                        matched.append({
                            "incident_id": meta.get("incident_id"),
                            "type": meta.get("type"),
                            "severity": meta.get("severity"),
                            "severity_score": meta.get("severity_score"),
                            "location": meta.get("location"),
                            "timestamp": meta.get("timestamp"),
                            "summary": doc
                        })
                    return matched
            except Exception:
                pass

        q_type = incident.get("type", "").lower()
        scored = []
        for doc in self.fallback_documents:
            meta = doc["metadata"]
            sim_score = 0.5
            if meta["type"].lower() == q_type:
                sim_score += 0.4
            if abs(meta["severity_score"] - incident.get("severity_score", 50)) < 20:
                sim_score += 0.2
            scored.append((sim_score, meta, doc["text"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "incident_id": item[1]["incident_id"],
                "type": item[1]["type"],
                "severity": item[1]["severity"],
                "severity_score": item[1]["severity_score"],
                "location": item[1]["location"],
                "timestamp": item[1]["timestamp"],
                "summary": item[2]
            }
            for item in scored[:top_k]
        ]

    def get_similar_incidents_text(self, incident: Dict[str, Any], top_k: int = 2) -> str:
        sims = self.find_similar_incidents(incident, top_k=top_k)
        if not sims:
            return "No historical matches found."
        summaries = [f"#{s.get('incident_id')} ({str(s.get('type')).upper()}, Severity {s.get('severity_score')}/100 at {s.get('location')}): {s.get('summary')}" for s in sims]
        return " | ".join(summaries)

global_rag_store = IncidentRAGStore()
