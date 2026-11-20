from pydantic import BaseModel,Field
from typing import Optional

class Task(BaseModel):
    id: int
    title: str 
    done : bool = False

class CreateTask(BaseModel):
    title: str = Field(...,min_length=1,description="title cannot empty")
    done: bool = False

class UpdateTask(BaseModel):
    title: Optional[str] = Field(None,description="title optional")
    done: Optional[bool] = None
