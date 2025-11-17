from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base, SessionLocal
from models import WeatherRecord, User
from schemas import WeatherRecordResponse, WeatherRecordUpdate, WeatherRecordBase, LoginRequest, LoginResponse, ChangePasswordRequest, ChangePasswordResponse
from auth import create_access_token, get_current_user, verify_password, get_password_hash
from datetime import date

# Create database tables
Base.metadata.create_all(bind=engine)

# Import initialization function
def init_database():
    """Initialize database with sample data if empty"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_records = db.query(WeatherRecord).count()
        existing_users = db.query(User).count()
        
        if existing_records > 0 and existing_users > 0:
            return
        
        # Sample weather data
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
        
        # Add sample weather data
        if existing_records == 0:
            for data in sample_data:
                record = WeatherRecord(**data)
                db.add(record)
        
        # Add admin user - always ensure admin exists with valid password
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            # Delete existing admin to recreate with fresh password (avoid password issues)
            db.delete(existing_admin)
        # Create new admin user
        try:
            hashed_password = get_password_hash("admin")
            admin_user = User(
                username="admin",
                password=hashed_password,
                role="admin"
            )
            db.add(admin_user)
        except Exception as e:
            print(f"Error creating admin user in init_database: {e}")
            raise
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

# Initialize database on startup if empty
init_database()

app = FastAPI(
    title="Weather App API",
    description="API for managing weather temperature records",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zai-weatherapp-frontend.onrender.com",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Weather App API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint for user authentication.
    
    - **username**: Username for login
    - **password**: Password for login
    
    Returns user data with id, username, role, and JWT token.
    """
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password hash
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return LoginResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        token=access_token
    )


@app.post("/change_password", response_model=ChangePasswordResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user password.
    
    Requires authentication (Bearer token).
    
    - **old_password**: Current password
    - **new_password**: New password to set
    
    Returns success message.
    """
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(status_code=401, detail="Invalid old password")
    
    # Check if new password is the same as old password
    if password_data.old_password == password_data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from old password")
    
    # Hash new password
    hashed_new_password = get_password_hash(password_data.new_password)
    
    # Update password
    current_user.password = hashed_new_password
    db.commit()
    
    return ChangePasswordResponse(message="Password changed successfully")


@app.get("/weather", response_model=List[WeatherRecordResponse])
async def get_all_weather_records(db: Session = Depends(get_db)):
    """
    Get all weather records from the database.
    
    Returns a list of all weather records with id, city_name, date, and temperature.
    """
    records = db.query(WeatherRecord).order_by(WeatherRecord.date, WeatherRecord.city_name).all()
    return records


@app.post("/weather", response_model=WeatherRecordResponse)
async def create_weather_record(
    record: WeatherRecordBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new weather record.
    
    Requires authentication (Bearer token).
    
    - **city_name**: Name of the city
    - **date**: Date of the measurement
    - **temperature**: Temperature value
    
    Returns the created weather record with generated ID.
    """
    db_record = WeatherRecord(
        city_name=record.city_name,
        date=record.date,
        temperature=record.temperature
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@app.put("/weather", response_model=WeatherRecordResponse)
async def update_weather_record(
    record_update: WeatherRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a weather record using the ID from the request body.
    
    Requires authentication (Bearer token).
    
    - **record_update**: The updated record data (id, city_name, date, temperature)
    
    Returns the updated weather record.
    """
    # Get the existing record
    db_record = db.query(WeatherRecord).filter(WeatherRecord.id == record_update.id).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    # Update the record
    db_record.city_name = record_update.city_name
    db_record.date = record_update.date
    db_record.temperature = record_update.temperature
    
    db.commit()
    db.refresh(db_record)
    
    return db_record


@app.delete("/weather/{record_id}")
async def delete_weather_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a weather record by ID.
    
    Requires authentication (Bearer token).
    
    - **record_id**: The ID of the record to delete
    
    Returns a success message.
    """
    db_record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    db.delete(db_record)
    db.commit()
    
    return {"message": "Weather record deleted successfully", "id": record_id}


def _initialize_database():
    """Internal function to initialize database"""
    db = SessionLocal()
    try:
        existing_records = db.query(WeatherRecord).count()
        existing_users = db.query(User).count()
        
        records_created = 0
        users_created = 0
        
        if existing_records == 0:
            sample_data = [
                {"id": 1, "city_name": "New York", "date": date(2025, 1, 14), "temperature": 5.0},
                {"id": 2, "city_name": "London", "date": date(2025, 1, 14), "temperature": 8.0},
                {"id": 3, "city_name": "Tokyo", "date": date(2025, 1, 14), "temperature": 12.0},
                {"id": 4, "city_name": "Paris", "date": date(2025, 1, 14), "temperature": 6.0},
                {"id": 5, "city_name": "New York", "date": date(2025, 1, 15), "temperature": 7.0},
                {"id": 6, "city_name": "London", "date": date(2025, 1, 15), "temperature": 9.0},
                {"id": 7, "city_name": "Tokyo", "date": date(2025, 1, 15), "temperature": 13.0},
                {"id": 8, "city_name": "Paris", "date": date(2025, 1, 15), "temperature": 7.0},
                {"id": 9, "city_name": "New York", "date": date(2025, 1, 16), "temperature": 6.0},
                {"id": 10, "city_name": "London", "date": date(2025, 1, 16), "temperature": 10.0},
                {"id": 11, "city_name": "Tokyo", "date": date(2025, 1, 16), "temperature": 14.0},
                {"id": 12, "city_name": "Paris", "date": date(2025, 1, 16), "temperature": 8.0},
            ]
            
            for data in sample_data:
                record = WeatherRecord(**data)
                db.add(record)
            records_created = len(sample_data)
        
        # Always ensure admin user exists with valid password
        # Delete existing admin user if it exists to avoid any password issues
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            # Delete existing admin to recreate with fresh password
            db.delete(existing_admin)
            db.commit()
        
        # Check if admin user doesn't exist, create it
        existing_admin_check = db.query(User).filter(User.username == "admin").first()
        if not existing_admin_check:
            # Create new admin user with hashed password
            # Use a simple, short password "admin" which is definitely < 72 bytes
            password_plain = "admin"
            
            # Debug: verify password length
            password_bytes = password_plain.encode('utf-8')
            print(f"DEBUG: Creating admin user with password length: {len(password_bytes)} bytes")
            print(f"DEBUG: Password: '{password_plain}'")
            
            try:
                hashed_password = get_password_hash(password_plain)
                
                # Debug: verify hash length
                print(f"DEBUG: Hash length: {len(hashed_password)} characters")
                print(f"DEBUG: Hash starts with: {hashed_password[:20]}...")
                
                admin_user = User(
                    username="admin",
                    password=hashed_password,
                    role="admin"
                )
                db.add(admin_user)
                users_created = 1
            except Exception as hash_error:
                # Log detailed error information
                error_type = type(hash_error).__name__
                error_msg = str(hash_error) if str(hash_error) else repr(hash_error)
                error_detail = f"{error_type}: {error_msg}"
                print(f"ERROR creating admin user: {error_detail}")
                print(f"ERROR password_plain type: {type(password_plain)}, value: '{password_plain}', bytes: {len(password_plain.encode('utf-8'))}")
                raise Exception(f"Failed to create admin user - {error_detail}")
        
        db.commit()
        
        return {
            "success": records_created > 0 or users_created > 0,
            "weather_records_created": records_created,
            "users_created": users_created,
            "existing_records": existing_records,
            "existing_users": existing_users
        }
            
    except HTTPException:
        # Re-raise HTTPException as-is
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        # Create detailed error message
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else repr(e)
        error_detail = f"{error_type}: {error_msg}" if error_msg else f"{error_type} (no message)"
        print(f"Error in _initialize_database: {error_detail}")
        raise Exception(f"Error initializing database - {error_detail}")
    finally:
        db.close()


@app.get("/init-db")
async def initialize_database_get():
    """
    Initialize database with sample data (GET endpoint).
    
    Only initializes if database is empty. Works without authentication for convenience.
    In production, consider using POST /init-db with authentication.
    
    Returns success message with number of records created.
    """
    try:
        result = _initialize_database()
        
        if result["success"]:
            return {
                "message": "Database initialized successfully",
                "weather_records_created": result["weather_records_created"],
                "users_created": result["users_created"]
            }
        else:
            return {
                "message": "Database already contains data",
                "existing_records": result["existing_records"],
                "existing_users": result["existing_users"]
            }
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else repr(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing database - {error_type}: {error_msg}"
        )


@app.post("/init-db")
async def initialize_database_post(current_user: User = Depends(get_current_user)):
    """
    Initialize database with sample data (POST endpoint).
    
    Requires authentication (Bearer token).
    Only initializes if database is empty.
    
    Returns success message with number of records created.
    """
    try:
        result = _initialize_database()
        
        if result["success"]:
            return {
                "message": "Database initialized successfully",
                "weather_records_created": result["weather_records_created"],
                "users_created": result["users_created"]
            }
        else:
            return {
                "message": "Database already contains data",
                "existing_records": result["existing_records"],
                "existing_users": result["existing_users"]
            }
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else repr(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing database - {error_type}: {error_msg}"
        )

