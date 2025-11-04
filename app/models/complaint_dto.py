from pydantic import BaseModel
from typing import Optional

class ComplaintRequest(BaseModel):
    citizen_name: str
    message: str
    complaint_type: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: int
    citizen_name: str
    message: str
    complaint_type: Optional[str]
    reply: Optional[str]
    action_taken: Optional[str]

    class Config:
        from_attributes  = True
