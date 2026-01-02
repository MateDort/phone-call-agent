"""Setup script to initialize the elderly care database."""
from database import Database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Initialize database with user data."""
    logger.info("Setting up elderly care database...")
    
    db = Database("elderly_care.db")
    
    # Initialize user bio (Máté Dort)
    logger.info("Setting up user bio...")
    bio_data = {
        "name": "Máté Dort",
        "birth_year": "2003",
        "birthplace": "Dunaújváros, Hungary",
        "hometown": "Kisapostag, Hungary",
        "current_location": "United States",
        "age": "21",
        "education": "Life University, graduating 2026",
        "background": "Born in 2003 in Dunaújváros, raised in Kisapostag, Hungary. Started swimming at age 3 and became a top competitor in the U.S., placing 2nd nationally by 0.07 seconds. Moved to the U.S. at 19 to pursue bigger dreams.",
        "achievements": "Built TapMate glasses at 21, competed in and placed at hackathons, became a top swimming competitor",
        "values": "Discipline, tradition, craftsmanship, personal growth, health, family relationships, and meaningful connections. Rejects social media and distractions.",
        "interests": "Design, invention, engineering, programming, swimming, marathons, languages, vintage style (50s-60s suits), reading physical books, writing on paper",
        "goals": "Become an iconic designer-inventor, build inventions that improve lives, travel the world in a custom van while creating products, achieve financial freedom by 30, explore life deeply",
        "personality": "Competitive, disciplined, curious, humorous, intelligent, deep thinker. Multi-skill creator learning fast and acting bold.",
        "routine": "Early mornings, early nights, consistent structure, trains regularly, eats clean, lives with clarity",
        "inspiration": "Steve Jobs, Ryo Lu, Tony Stark (fictional)"
    }
    
    for key, value in bio_data.items():
        db.set_bio(key, value)
    
    logger.info("✓ User bio initialized")
    
    # Add Helen's contact
    logger.info("Setting up contacts...")
    existing_contact = db.search_contact("Helen")
    if not existing_contact:
        db.add_contact(
            name="Helen Stadler",
            relation="Girlfriend",
            phone="404-953-5533",
            birthday="2004-08-27",
            notes="Birthday: August 27, 2004"
        )
        logger.info("✓ Added Helen Stadler to contacts")
    else:
        logger.info("✓ Helen Stadler already in contacts")
    
    # Add example reminder
    logger.info("Setting up example reminders...")
    existing_reminders = db.get_reminders()
    if not existing_reminders:
        from datetime import datetime, timedelta
        
        # Add a reminder for tomorrow at 3pm as an example
        tomorrow = datetime.now() + timedelta(days=1)
        reminder_time = tomorrow.replace(hour=15, minute=0, second=0, microsecond=0)
        
        db.add_reminder(
            title="Take afternoon medication",
            datetime_str=reminder_time.isoformat(),
            recurrence=None,
            days_of_week=None
        )
        logger.info(f"✓ Added example reminder for {reminder_time}")
    else:
        logger.info(f"✓ Found {len(existing_reminders)} existing reminder(s)")
    
    db.close()
    
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE SETUP COMPLETE!")
    logger.info("=" * 60)
    logger.info("✓ User bio: Máté Dort")
    logger.info("✓ Contacts: Helen Stadler (Girlfriend)")
    logger.info("✓ Reminders: Ready to use")
    logger.info("=" * 60)
    logger.info("\nYou can now run: python main_elderly.py")


if __name__ == "__main__":
    setup_database()

