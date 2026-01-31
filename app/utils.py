from sqlalchemy.orm import Session
from app.models import Business, Review


def compute_aggregated_vibe_score(business_id: int, database_session: Session) -> float:
    """
    Compute the aggregated Vibe Score for a business from all reviews.
    
    Parameters:
        business_id: The ID of the business
        database_session: Active database session
        
    Returns:
        The average vibe score (0-100)
    """
    all_reviews = database_session.query(Review).filter(
        Review.business_id == business_id
    ).all()
    
    if not all_reviews:
        return 0.0
    
    # Get reviews with valid vibe scores
    scores = [r.vibe_score for r in all_reviews if r.vibe_score is not None]
    
    if not scores:
        return 0.0
    
    # Calculate mean
    average = sum(scores) / len(scores)
    return round(average, 2)


def refresh_business_metrics(business_id: int, database_session: Session):
    """
    Refresh the aggregated metrics for a business.
    
    Parameters:
        business_id: The ID of the business
        database_session: Active database session
    """
    target_business = database_session.query(Business).filter(
        Business.id == business_id
    ).first()
    
    if target_business:
        # Update vibe score
        target_business.aggregated_vibe_score = compute_aggregated_vibe_score(
            business_id, database_session
        )
        
        # Update review count
        review_count = database_session.query(Review).filter(
            Review.business_id == business_id
        ).count()
        target_business.total_reviews = review_count
        
        database_session.commit()


def analyze_review_sentiment(review_content: str) -> dict:
    """
    Analyze review sentiment using DS Service.
    
    Parameters:
        review_content: The text content of the review
        
    Returns:
        Dictionary with vibe_score, sentiment, and keywords
        
    NOTE: This is a placeholder. Replace with actual DS Service API call.
    """
    # TODO: Implement DS Service integration
    # Example:
    # import requests
    # response = requests.post(DS_SERVICE_ENDPOINT, json={"text": review_content})
    # return response.json()
    
    return {
        "vibe_score": None,
        "sentiment": None,
        "keywords": None
    }
