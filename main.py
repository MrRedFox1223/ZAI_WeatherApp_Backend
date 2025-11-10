from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import WeatherRecord, User
from schemas import WeatherRecordResponse, WeatherRecordUpdate, WeatherRecordBase, LoginRequest, LoginResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Weather App API",
    description="API for managing weather temperature records",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
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
    
    Returns user data with id, username, role, and token (currently empty).
    """
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Simple password check (in production, use hashed passwords)
    if user.password != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return LoginResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        token=""  # Token is empty for now
    )


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
    db: Session = Depends(get_db)
):
    """
    Create a new weather record.
    
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
    db: Session = Depends(get_db)
):
    """
    Update a weather record using the ID from the request body.
    
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
    db: Session = Depends(get_db)
):
    """
    Delete a weather record by ID.
    
    - **record_id**: The ID of the record to delete
    
    Returns a success message.
    """
    db_record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Weather record not found")
    
    db.delete(db_record)
    db.commit()
    
    return {"message": "Weather record deleted successfully", "id": record_id}

