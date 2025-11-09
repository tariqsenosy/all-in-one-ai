from fastapi import APIRouter, Depends
from app.models.complaint_dto import ComplaintRequest, ComplaintResponse
from app.services.complaint_service import ComplaintService
from app.core.dependencies import get_complaint_service
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
router = APIRouter()

@router.post("/", response_model=ComplaintResponse)
async def submit_complaint(
    request: ComplaintRequest,
    service: ComplaintService = Depends(get_complaint_service)
):
    return await service.handle_complaint(request)

@router.post("/voice", response_model=ComplaintResponse)
async def create_voice_complaint(
    citizen_name: str = Form(...),
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    service = ComplaintService(db)
    return await service.handle_voice_complaint(citizen_name, audio_file)