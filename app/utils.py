from sqlalchemy.orm import Session
from app.models import Business, Review
import requests
from app.config import DS_SERVICE_ENDPOINT


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
    Analyze review sentiment using keyword-based scoring.
    
    Parameters:
        review_content: The text content of the review
        
    Returns:
        Dictionary with vibe_score, sentiment, and keywords (as JSON string)
    """
    import json
    
    # Convert to lowercase for analysis
    review_lower = review_content.lower()
    
    # Define sentiment keywords
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'awesome', 'fantastic', 'wonderful',
        'love', 'best', 'perfect', 'brilliant', 'outstanding', 'superb', 'exceptional',
        'impressed', 'satisfied', 'happy', 'friendly', 'clean', 'nice', 'pleasant',
        'delicious', 'tasty', 'professional', 'quick', 'efficient', 'helpful', 'recommend'
    }
    
    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'poor', 'disgusting',
        'rude', 'slow', 'dirty', 'overpriced', 'disappointing', 'waste', 'useless',
        'unprofessional', 'broken', 'uncomfortable', 'cold', 'bland', 'stale',
        'quit', 'avoid', 'disgusted', 'angry', 'frustrated', 'disappointed',
        'below', 'subpar', 'lacking', 'missing', 'incomplete', 'mediocre'
    }
    
    # Check for negative phrases (higher weight)
    negative_phrases = [
        'not good', 'not great', 'not recommended', 'not worth',
        'don\'t recommend', 'would not', 'will not', 'never again', 'extremely disappointed', 'highly disappointed','waste of time'
    ]
    
    positive_phrases = [
        'highly recommend', 'would recommend', 'definitely recommend'
    ]
    
    # Count positive and negative words
    positive_count = sum(1 for word in positive_words if ' ' + word + ' ' in ' ' + review_lower + ' ')
    negative_count = sum(1 for word in negative_words if ' ' + word + ' ' in ' ' + review_lower + ' ')
    
    # Check for phrases (weighted heavier)
    positive_phrase_count = sum(2 for phrase in positive_phrases if phrase in review_lower)
    negative_phrase_count = sum(2 for phrase in negative_phrases if phrase in review_lower)
    
    # Calculate vibe score (0-100)
    # Base score of 50 (neutral), +15 per positive word, -15 per negative word
    # Phrases count as 2x weight
    vibe_score = 50 + (positive_count * 15) + (positive_phrase_count * 15) - (negative_count * 15) - (negative_phrase_count * 15)
    vibe_score = max(0, min(100, vibe_score))  # Clamp between 0-100
    
    # Determine sentiment
    if vibe_score >= 65:
        sentiment = "positive"
    elif vibe_score >= 40:
        sentiment = "neutral"
    else:
        sentiment = "negative"
    
    # Extract keywords (words longer than 4 characters)
    words = review_content.lower().split()
    keywords_list = [w.strip('.,!?;:') for w in words if len(w) > 4][:5]
    
    # Convert keywords to JSON string for storage
    keywords_json = json.dumps(keywords_list)
    
    return {
        "vibe_score": vibe_score,
        "sentiment": sentiment,
        "keywords": keywords_json
    }
