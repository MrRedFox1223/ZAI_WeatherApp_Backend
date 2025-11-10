"""
Script to initialize the database with sample data.
Run this script once to populate the database with initial weather records.
"""
from database import SessionLocal, engine
from models import Base, WeatherRecord, User
from datetime import date
from auth import get_password_hash

# Create all tables
Base.metadata.create_all(bind=engine)

# Sample data
sample_data = [
    {"id": 1, "city_name": "New York", "date": date(2024, 1, 14), "temperature": 5.0},
    {"id": 2, "city_name": "London", "date": date(2024, 1, 14), "temperature": 8.0},
    {"id": 3, "city_name": "Tokyo", "date": date(2024, 1, 14), "temperature": 12.0},
    {"id": 4, "city_name": "Paris", "date": date(2024, 1, 14), "temperature": 6.0},
    {"id": 5, "city_name": "New York", "date": date(2024, 1, 15), "temperature": 7.0},
    {"id": 6, "city_name": "London", "date": date(2024, 1, 15), "temperature": 9.0},
    {"id": 7, "city_name": "Tokyo", "date": date(2024, 1, 15), "temperature": 13.0},
    {"id": 8, "city_name": "Paris", "date": date(2024, 1, 15), "temperature": 7.0},
    {"id": 9, "city_name": "New York", "date": date(2024, 1, 16), "temperature": 6.0},
    {"id": 10, "city_name": "London", "date": date(2024, 1, 16), "temperature": 10.0},
    {"id": 11, "city_name": "Tokyo", "date": date(2024, 1, 16), "temperature": 14.0},
    {"id": 12, "city_name": "Paris", "date": date(2024, 1, 16), "temperature": 8.0},
]

def init_db():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_records = db.query(WeatherRecord).count()
        existing_users = db.query(User).count()
        
        if existing_records > 0 and existing_users > 0:
            print(f"Database already contains {existing_records} weather records and {existing_users} users. Skipping initialization.")
            return
        
        # Add sample weather data
        if existing_records == 0:
            for data in sample_data:
                record = WeatherRecord(**data)
                db.add(record)
            print(f"Successfully initialized database with {len(sample_data)} weather records.")
        
        # Add admin user
        if existing_users == 0:
            hashed_password = get_password_hash("admin")
            admin_user = User(
                username="admin",
                password=hashed_password,
                role="admin"
            )
            db.add(admin_user)
            print("Successfully added admin user (username: admin, password: admin - hashed).")
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

