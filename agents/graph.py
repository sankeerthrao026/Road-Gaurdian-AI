from typing import Dict, Any, TypedDict, Optional, List
from severity.scorer import score_incident
from agents.state import global_incident_store
from agents.response_agent import ResponseAgent
from agents.evidence_agent import EvidenceAgent
from agents.report_agent import ReportAgent

class IncidentState(TypedDict):
    raw_incident: Dict[str, Any]
    frame_image: Optional[Any]
    scored_incident: Optional[Dict[str, Any]]
    dispatches: Optional[List[Dict[str, Any]]]
    evidence: Optional[Dict[str, Any]]
    report: Optional[str]
    similar_context: Optional[str]
    priority_rank: Optional[int]

def incident_analysis_node(state: IncidentState) -> IncidentState:
    raw = state["raw_incident"]
    if "features" not in raw:
        raw["features"] = {
            "vehicle_count": 1,
            "person_on_road": False,
            "fire_smoke": False,
            "rollover": False,
            "traffic_impact": "low"
        }
    state["raw_incident"] = raw
    return state

def severity_agent_node(state: IncidentState) -> IncidentState:
    incident = dict(state["raw_incident"])
    features = incident.get("features", {})
    score_res = score_incident(features)

    incident["severity_score"] = score_res["severity_score"]
    incident["severity_label"] = score_res["severity_label"]
    incident["shap_values"] = score_res["shap_values"]
    incident["model_used"] = score_res["model_used"]

    state["scored_incident"] = incident
    return state

def prioritization_agent_node(state: IncidentState) -> IncidentState:
    incident = state["scored_incident"]
    updated_incident = global_incident_store.upsert_incident(incident)
    state["priority_rank"] = updated_incident.get("priority_rank", 1)
    state["scored_incident"] = updated_incident
    return state

def response_agent_node(state: IncidentState) -> IncidentState:
    incident = state["scored_incident"]
    dispatches = ResponseAgent.plan_response(incident)
    for d in dispatches:
        global_incident_store.add_dispatch(d)
    state["dispatches"] = dispatches
    return state

def evidence_agent_node(state: IncidentState) -> IncidentState:
    incident = state["scored_incident"]
    inc_id = incident.get("incident_id", "UNKNOWN")
    evidence_agent = EvidenceAgent()
    evidence_payload = evidence_agent.capture_evidence(
        incident_id=inc_id,
        frame_image=state.get("frame_image")
    )
    incident["evidence"] = evidence_payload
    state["evidence"] = evidence_payload
    state["scored_incident"] = incident
    global_incident_store.upsert_incident(incident)
    return state

def report_agent_node(state: IncidentState) -> IncidentState:
    incident = state["scored_incident"]
    report_text = ReportAgent.generate_report(incident, similar_context=state.get("similar_context", ""))
    incident["report_text"] = report_text
    state["report"] = report_text
    state["scored_incident"] = incident
    global_incident_store.upsert_incident(incident)
    return state

def build_agent_graph():
    try:
        from langgraph.graph import StateGraph, END
        workflow = StateGraph(IncidentState)

        workflow.add_node("IncidentAnalysis", incident_analysis_node)
        workflow.add_node("SeverityAgent", severity_agent_node)
        workflow.add_node("PrioritizationAgent", prioritization_agent_node)
        workflow.add_node("ResponseAgent", response_agent_node)
        workflow.add_node("EvidenceAgent", evidence_agent_node)
        workflow.add_node("ReportAgent", report_agent_node)

        workflow.set_entry_point("IncidentAnalysis")
        workflow.add_edge("IncidentAnalysis", "SeverityAgent")
        workflow.add_edge("SeverityAgent", "PrioritizationAgent")
        workflow.add_edge("PrioritizationAgent", "ResponseAgent")
        workflow.add_edge("ResponseAgent", "EvidenceAgent")
        workflow.add_edge("EvidenceAgent", "ReportAgent")
        workflow.add_edge("ReportAgent", END)

        return workflow.compile()
    except Exception as e:
        return None

_compiled_graph = None

def process_incident_through_agents(
    incident_data: Dict[str, Any],
    frame_image: Optional[Any] = None,
    similar_context: str = ""
) -> Dict[str, Any]:
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_agent_graph()

    initial_state: IncidentState = {
        "raw_incident": incident_data,
        "frame_image": frame_image,
        "scored_incident": None,
        "dispatches": None,
        "evidence": None,
        "report": None,
        "similar_context": similar_context,
        "priority_rank": 1
    }

    if _compiled_graph is not None:
        try:
            final_state = _compiled_graph.invoke(initial_state)
            return final_state["scored_incident"]
        except Exception:
            pass

    s1 = incident_analysis_node(initial_state)
    s2 = severity_agent_node(s1)
    s3 = prioritization_agent_node(s2)
    s4 = response_agent_node(s3)
    s5 = evidence_agent_node(s4)
    s6 = report_agent_node(s5)
    return s6["scored_incident"]
