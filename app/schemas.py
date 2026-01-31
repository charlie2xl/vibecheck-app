from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Business schemas
class BusinessResponse(BaseModel):
    id: int
    name: str
    category: str
    location: str
    aggregated_vibe_score: float
    total_reviews: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Review schemas
class ReviewCreate(BaseModel):
    content: str = Field(..., min_length=10)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    business_id: int
    content: str
    vibe_score: Optional[float]
    sentiment: Optional[str]
    keywords: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# General response schemas
class MessageResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
