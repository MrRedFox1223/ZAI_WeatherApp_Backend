from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base, SessionLocal
from models import WeatherRecord, User
from schemas import WeatherRecordResponse, WeatherRecordUpdate, WeatherRecordBase, LoginRequest, LoginResponse, ChangePasswordRequest, ChangePasswordResponse
from auth import create_access_token, get_current_user, verify_password, get_password_hash
from init_db import generate_sample_data

# Create database tables
Base.metadata.create_all(bind=engine)


def init_database():
    """Initialize database with sample data if empty"""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_records = db.query(WeatherRecord).count()
        existing_users = db.query(User).count()
        
        if existing_records > 0 and existing_users > 0:
            return
        
        # Generate and add sample weather data
        if existing_records == 0:
            sample_data = generate_sample_data()
            for data in sample_data:
                record = WeatherRecord(**data)
                db.add(record)
        
        # Add admin user if it doesn't exist
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            hashed_password = get_password_hash("admin")
            admin_user = User(
                username="admin",
                password=hashed_password,
                role="admin"
            )
            db.add(admin_user)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise
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
