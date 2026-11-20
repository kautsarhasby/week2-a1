from pydantic import BaseModel,Field
from typing import Optional

class AuthRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None