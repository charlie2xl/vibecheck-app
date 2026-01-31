from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, initialize_database
from app.models import User, Business, Review
from app.schemas import (
    UserCreate, UserLogin, UserResponse, LoginResponse,
    BusinessResponse, ReviewCreate, ReviewResponse, MessageResponse
)
from app.auth import hash_password, verify_password
from app.utils import analyze_review_sentiment, refresh_business_metrics

# Create FastAPI application
app = FastAPI(title="VibeCheck Business Platform", version="1.0.0")


# Startup event handler
@app.on_event("startup")
def on_startup():
    initialize_database()


# Root route
@app.get("/")
def home():
    return {"status": "active", "message": "VibeCheck Business Platform API"}


# User registration endpoint
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_new_user(user_info: UserCreate, db: Session = Depends(get_db)):
    # Check username availability
    username_exists = db.query(User).filter(User.username == user_info.username).first()
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken"
        )
    
    # Check email availability
    email_exists = db.query(User).filter(User.email == user_info.email).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered"
        )
    
    # Hash password and create user
    password_hash = hash_password(user_info.password)
    user_instance = User(
        username=user_info.username,
        email=user_info.email,
        hashed_password=password_hash
    )
    
    db.add(user_instance)
    db.commit()
    db.refresh(user_instance)
    
    return user_instance


# User login endpoint
@app.post("/login", response_model=LoginResponse)
def authenticate_user(login_info: UserLogin, db: Session = Depends(get_db)):
    # Retrieve user from database
    user_account = db.query(User).filter(User.username == login_info.username).first()
    
    if not user_account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Validate password
    password_valid = verify_password(login_info.password, user_account.hashed_password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return {
        "message": "Authentication successful",
        "user": user_account
    }


# List all businesses endpoint
@app.get("/businesses", response_model=List[BusinessResponse])
def list_businesses(db: Session = Depends(get_db)):
    business_list = db.query(Business).all()
    return business_list


# Get single business endpoint
@app.get("/businesses/{business_id}", response_model=BusinessResponse)
def retrieve_business(business_id: int, db: Session = Depends(get_db)):
    business_record = db.query(Business).filter(Business.id == business_id).first()
    
    if not business_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    return business_record


# Create review endpoint
@app.post("/businesses/{business_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    business_id: int,
    review_info: ReviewCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Validate business existence
    business_record = db.query(Business).filter(Business.id == business_id).first()
    if not business_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} does not exist"
        )
    
    # Validate user existence
    user_record = db.query(User).filter(User.id == user_id).first()
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} does not exist"
        )
    
    # Analyze sentiment using DS Service
    sentiment_analysis = analyze_review_sentiment(review_info.content)
    
    # Create review record
    review_instance = Review(
        user_id=user_id,
        business_id=business_id,
        content=review_info.content,
        vibe_score=sentiment_analysis.get("vibe_score"),
        sentiment=sentiment_analysis.get("sentiment"),
        keywords=sentiment_analysis.get("keywords")
    )
    
    db.add(review_instance)
    db.commit()
    db.refresh(review_instance)
    
    # Update business metrics
    refresh_business_metrics(business_id, db)
    
    return review_instance


# Get reviews for business endpoint
@app.get("/businesses/{business_id}/reviews", response_model=List[ReviewResponse])
def fetch_business_reviews(business_id: int, db: Session = Depends(get_db)):
    # Check if business exists
    business_record = db.query(Business).filter(Business.id == business_id).first()
    if not business_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} does not exist"
        )
    
    # Get all reviews
    review_list = db.query(Review).filter(Review.business_id == business_id).all()
    return review_list
