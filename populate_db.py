"""
Database Population Script for VibeCheck Business
Run this script ONLY after migrations have been applied.

Usage:
    python scripts/populate_db.py
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Business


def populate_database():
    """
    Populate the database with sample businesses.
    """
    db: Session = SessionLocal()

    try:
        existing_count = db.query(Business).count()

        if existing_count > 0:
            print(f"Database already contains {existing_count} businesses.")
            user_input = input("Do you want to add more businesses anyway? (yes/no): ")
            if user_input.lower() not in ("yes", "y"):
                print("Operation cancelled.")
                return

        sample_businesses = [
            {
                "name": "Cosmic Coffee Roasters",
                "category": "Coffee Shop",
                "location": "742 Starlight Avenue, San Francisco, CA 94102",
            },
            {
                "name": "The Golden Spoon Diner",
                "category": "Restaurant",
                "location": "159 Heritage Road, Philadelphia, PA 19102",
            },
            {
                "name": "Elite Auto Solutions",
                "category": "Auto Repair",
                "location": "368 Mechanic Street, Detroit, MI 48201",
            },
            {
                "name": "Zen Balance Fitness",
                "category": "Fitness",
                "location": "951 Harmony Lane, Phoenix, AZ 85001",
            },
            {
                "name": "Circuit City Electronics",
                "category": "Electronics Store",
                "location": "753 Digital Plaza, San Jose, CA 95101",
            },
            {
                "name": "Chic Avenue Clothing",
                "category": "Fashion Retail",
                "location": "246 Fashion Boulevard, New York, NY 10001",
            },
            {
                "name": "Pawsitive Pet Care",
                "category": "Pet Services",
                "location": "802 Animal Way, Houston, TX 77001",
            },
            {
                "name": "Sunrise Artisan Bakery",
                "category": "Bakery",
                "location": "135 Baker Street, Minneapolis, MN 55401",
            },
            {
                "name": "Sharp Styles Barber Lounge",
                "category": "Barbershop",
                "location": "579 Clipper Avenue, Las Vegas, NV 89101",
            },
            {
                "name": "Chapter & Verse Bookshop",
                "category": "Bookstore",
                "location": "913 Literary Lane, Seattle, WA 98101",
            },
            {
                "name": "Harvest Fresh Market",
                "category": "Grocery Store",
                "location": "468 Produce Place, Charlotte, NC 28201",
            },
            {
                "name": "Serenity Wellness Spa",
                "category": "Spa",
                "location": "824 Tranquil Trail, Tampa, FL 33601",
            },
            {
                "name": "Mountain Peak Adventure Gear",
                "category": "Outdoor Equipment",
                "location": "357 Summit Street, Denver, CO 80201",
            },
            {
                "name": "Melody Music Academy",
                "category": "Music School",
                "location": "691 Harmony Avenue, Nashville, TN 37201",
            },
        ]

        businesses = [
            Business(
                name=b["name"],
                category=b["category"],
                location=b["location"],
                aggregated_vibe_score=0.0,
                total_reviews=0,
            )
            for b in sample_businesses
        ]

        db.add_all(businesses)
        db.commit()

        print(f"\n✓ Successfully added {len(businesses)} businesses.\n")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Error occurred: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("VibeCheck Business — Database Population")
    print("=" * 60)
    populate_database()
    print("=" * 60)
