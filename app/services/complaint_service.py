from sqlalchemy.ext.asyncio import AsyncSession
from app.models.complaint_model import Complaint
from app.ai.complaint_responder import ComplaintResponder
from app.models.complaint_dto import ComplaintRequest, ComplaintResponse
from app.ai.complaint_classifier import ComplaintClassifier
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Optional
import asyncio
import tempfile
import os
import whisper


# =========================
#   Define the graph state
# =========================
class ComplaintState(TypedDict):
    citizen_name: str
    message: str
    complaint_type: str
    reply: str
    action_taken: str
    db: AsyncSession
    saved_complaint: Complaint | None


# =========================
#   Whisper global model
# =========================
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
_whisper_model = whisper.load_model(WHISPER_MODEL_NAME)


# =========================
#   Complaint Service
# =========================
class ComplaintService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.classifier = ComplaintClassifier()
        self.responder = ComplaintResponder()
        self.graph = self._build_graph()
        self.transcriber = whisper.load_model("base")  # load local Whisper model

    # -------------------------
    # Step 1: classify complaint
    # -------------------------
    async def _classify_node(self, state: ComplaintState) -> ComplaintState:
        complaint_type = self.classifier.classify_complaint(state["message"])
        state["complaint_type"] = complaint_type
        return state

       # Step 2: توليد رد بشري طبيعي
    async def _reply_node(self, state: ComplaintState) -> ComplaintState:
        reply_text = self.responder.generate_reply(
            citizen_name=state["citizen_name"],
            complaint_text=state["message"],
            complaint_type=state["complaint_type"]
        )
        state["reply"] = reply_text
        state["action_taken"] = "AI Responded"
        return state

    # -------------------------
    # Step 3: persist to DB
    # -------------------------
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

    # -------------------------
    # Build the LangGraph flow
    # -------------------------
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

    # -------------------------
    # Handle text complaint
    # -------------------------
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

    # -------------------------
    # Handle voice complaint
    # -------------------------
    async def handle_voice_complaint(self, citizen_name: str, audio_file) -> ComplaintResponse:
        # Step 1: save temporary audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await audio_file.read())
            tmp_path = tmp.name

        # Step 2: transcribe audio
        transcript = await self._transcribe_audio(tmp_path)
        print("Transcript:", transcript)

        # Step 3: reuse text complaint flow
        complaint_request = ComplaintRequest(
            citizen_name=citizen_name,
            message=transcript
        )
        return await self.handle_complaint(complaint_request)

    # -------------------------
    # Transcribe audio (local Whisper)
    # -------------------------
    async def _transcribe_audio(self, file_path: str, language: Optional[str] = "en") -> str:
        """Transcribe audio file using local Whisper model."""

        def blocking_transcribe(path: str, lang: Optional[str]):
            return _whisper_model.transcribe(path, language=lang, task="transcribe", temperature=0.0)

        result = await asyncio.to_thread(blocking_transcribe, file_path, language)

        raw_text = result.get("text", "").strip()
        print("WHISPER raw text:", repr(raw_text))
        segments = result.get("segments", [])
        print(f"WHISPER segments count: {len(segments)}")
        for i, seg in enumerate(segments):
            print(f"SEGMENT {i}: [{seg.get('start', 0):.2f} - {seg.get('end', 0):.2f}] {repr(seg.get('text'))}")

        return raw_text
