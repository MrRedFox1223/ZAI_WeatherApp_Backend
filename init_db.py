from database import SessionLocal, engine
from models import Base, WeatherRecord, User
from datetime import date
from auth import get_password_hash

Base.metadata.create_all(bind=engine)


def generate_sample_data():
    cities = [
        ("Warszawa", [-2.0, -1.0, 3.0, 9.0, 15.0, 18.0, 20.0, 19.0, 14.0, 8.0]),
        ("Berlin", [0.0, 1.0, 5.0, 10.0, 15.0, 18.0, 19.0, 19.0, 14.0, 9.0]),
        ("Paryż", [4.0, 5.0, 8.0, 11.0, 15.0, 18.0, 19.0, 19.0, 16.0, 12.0]),
        ("Rzym", [7.0, 8.0, 11.0, 14.0, 18.0, 22.0, 25.0, 25.0, 21.0, 16.0]),
        ("Madryt", [6.0, 8.0, 11.0, 13.0, 17.0, 22.0, 25.0, 25.0, 20.0, 14.0]),
        ("Londyn", [5.0, 5.0, 7.0, 10.0, 13.0, 16.0, 18.0, 18.0, 15.0, 11.0]),
        ("Tokio", [5.0, 6.0, 9.0, 14.0, 18.0, 22.0, 26.0, 27.0, 23.0, 17.0]),
        ("Nowy Jork", [0.0, 1.0, 5.0, 11.0, 17.0, 22.0, 25.0, 24.0, 20.0, 14.0]),
        ("Sydney", [23.0, 23.0, 22.0, 19.0, 16.0, 13.0, 12.0, 13.0, 15.0, 18.0]),
        ("Kair", [14.0, 15.0, 18.0, 22.0, 26.0, 28.0, 29.0, 29.0, 27.0, 24.0]),
    ]
    
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_data = []
    record_id = 1
    
    for city_name, temperatures in cities:
        for month_idx, month in enumerate(months):
            sample_data.append({
                "id": record_id,
                "city_name": city_name,
                "date": date(2025, month, 15),
                "temperature": temperatures[month_idx]
            })
            record_id += 1
    
    return sample_data


def init_db():
    db = SessionLocal()
    try:
        existing_records = db.query(WeatherRecord).count()
        existing_users = db.query(User).count()
        
        if existing_records > 0 and existing_users > 0:
            print(f"Database already contains {existing_records} weather records and {existing_users} users. Skipping initialization.")
            return
        
        if existing_records == 0:
            sample_data = generate_sample_data()
            for data in sample_data:
                record = WeatherRecord(**data)
                db.add(record)
            print(f"Successfully initialized database with {len(sample_data)} weather records.")
        
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

