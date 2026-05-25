from pydantic import BaseModel, Field
from uuid import UUID

class UserTestSchema(BaseModel):
    id: UUID
    username: str = Field(..., min_length=1, max_length=64)
    is_active: bool

class ItemTestSchema(BaseModel):
    id: UUID
    title: str = Field(..., min_length=1, max_length=128)
    user_id: UUID