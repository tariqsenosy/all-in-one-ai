from fastapi import APIRouter, Depends
from app.models.complaint_dto import ComplaintRequest, ComplaintResponse
from app.services.complaint_service import ComplaintService
from app.core.dependencies import get_complaint_service

router = APIRouter()

@router.post("/", response_model=ComplaintResponse)
async def submit_complaint(
    request: ComplaintRequest,
    service: ComplaintService = Depends(get_complaint_service)
):
    return await service.handle_complaint(request)
