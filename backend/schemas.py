from pydantic import BaseModel
from typing import List

class BusinessCreate(BaseModel):
    name: str
    category: str
    location: str

class ReviewCreate(BaseModel):
    business_id: int
    content: str

class ReviewResponse(ReviewCreate):
    id: int
    vibe_score: float
    sentiment: str

class VibeResult(BaseModel):
    vibe_score: float
    sentiment: str
    keywords: List[str]
