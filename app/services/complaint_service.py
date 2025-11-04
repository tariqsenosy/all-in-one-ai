from sqlalchemy.ext.asyncio import AsyncSession
from app.models.complaint_model import Complaint
from app.models.complaint_dto import ComplaintRequest, ComplaintResponse
from app.ai.complaint_classifier import ComplaintClassifier
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# Define the graph state
class ComplaintState(TypedDict):
    citizen_name: str
    message: str
    complaint_type: str
    reply: str
    action_taken: str
    db: AsyncSession
    saved_complaint: Complaint | None


class ComplaintService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.classifier = ComplaintClassifier()
        self.graph = self._build_graph()

    # Step 1: classify complaint type
    async def _classify_node(self, state: ComplaintState) -> ComplaintState:
        complaint_type = self.classifier.classify_complaint(state["message"])
        state["complaint_type"] = complaint_type
        return state

    # Step 2: generate AI reply
    async def _reply_node(self, state: ComplaintState) -> ComplaintState:
        complaint_type = state["complaint_type"]
        state["reply"] = f"Complaint categorized as '{complaint_type}'. A team will review it soon."
        state["action_taken"] = "AI Classified"
        return state

    # Step 3: persist to DB
    async def _save_node(self, state: ComplaintState) -> ComplaintState:
        db = state["db"]
        complaint = Complaint(
            citizen_name=state["citizen_name"],
            message=state["message"],
            complaint_type=state["complaint_type"],
            reply=state["reply"],
            action_taken=state["action_taken"],
        )
        db.add(complaint)
        await db.commit()
        await db.refresh(complaint)
        state["saved_complaint"] = complaint
        return state

    # Build the LangGraph flow
    def _build_graph(self):
        graph = StateGraph(ComplaintState)
        graph.add_node("classify", self._classify_node)
        graph.add_node("reply", self._reply_node)
        graph.add_node("save", self._save_node)

        graph.add_edge(START, "classify")
        graph.add_edge("classify", "reply")
        graph.add_edge("reply", "save")
        graph.add_edge("save", END)

        return graph.compile()

    # Public method (entry point)
    async def handle_complaint(self, request: ComplaintRequest) -> ComplaintResponse:
        initial_state: ComplaintState = {
            "citizen_name": request.citizen_name,
            "message": request.message,
            "complaint_type": "",
            "reply": "",
            "action_taken": "",
            "db": self.db,
            "saved_complaint": None,
        }

        # Run through the LangGraph pipeline
        final_state = await self.graph.ainvoke(initial_state)
        saved = final_state["saved_complaint"]

        return ComplaintResponse.from_orm(saved)
