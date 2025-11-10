from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    temperature = Column(Float, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="admin")

