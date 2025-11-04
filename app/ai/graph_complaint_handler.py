from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from app.ai.complaint_classifier import ComplaintClassifier
from app.models import Complaint
from sqlalchemy.ext.asyncio import AsyncSession

classifier = ComplaintClassifier()

class ComplaintState(TypedDict):
    citizen_name: str
    message: str
    category: str
    response: str
    action: str
    db: AsyncSession


# --- Node 1: classify complaint ---
async def classify_node(state: ComplaintState) -> ComplaintState:
    category = classifier.classify_complaint(state["message"])
    state["category"] = category
    return state


# --- Node 2: decide action ---
async def decide_action_node(state: ComplaintState) -> ComplaintState:
    routes = {
        "dogs": "Animal Control",
        "noise": "City Council",
        "cars": "Traffic Dept",
        "robbery": "Police",
        "assault": "Police",
        "utilities": "Utility Services",
        "city_services": "Municipality",
        "neighbor": "Neighborhood Committee"
    }
    category = state.get("category", "unknown")
    state["action"] = routes.get(category, "General Support")
    return state


# --- Node 3: generate response ---
async def response_node(state: ComplaintState) -> ComplaintState:
    state["response"] = (
        f"Complaint categorized as '{state['category']}'. "
        f"It has been routed to the {state['action']} department. "
        "A representative will review it soon."
    )
    return state


# --- Node 4: persist result to DB ---
async def persist_node(state: ComplaintState) -> ComplaintState:
    db: AsyncSession = state["db"]

    complaint = Complaint(
        citizen_name=state["citizen_name"],
        message=state["message"],
        complaint_type=state["category"],
        reply=state["response"],
        action_taken=state["action"],
    )

    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)
    state["saved_complaint"] = complaint
    return state


def build_complaint_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("classify", classify_node)
    graph.add_node("decide_action", decide_action_node)
    graph.add_node("generate_response", response_node)
    graph.add_node("persist", persist_node)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "decide_action")
    graph.add_edge("decide_action", "generate_response")
    graph.add_edge("generate_response", "persist")
    graph.add_edge("persist", END)

    return graph.compile()
