from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.complaint_service import ComplaintService

async def get_complaint_service(
    db: AsyncSession = Depends(get_session),
) -> ComplaintService:
    return ComplaintService(db)
