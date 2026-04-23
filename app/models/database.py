# app/models/database.py
"""Database models and connection (optional - for future use)"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class StaffModel(Base):
    """Staff database model"""
    __tablename__ = 'staff'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String)
    availability = Column(String)
    shift_preference = Column(String)
    max_hours = Column(Integer)
    experience_years = Column(Integer)
    skills = Column(String)
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

class ServiceUserModel(Base):
    """Service user database model"""
    __tablename__ = 'service_users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    primary_shift = Column(String)
    support_ratio = Column(Integer)
    days_per_week = Column(Integer)
    shift_duration = Column(Integer)
    location = Column(String)
    weekly_hours = Column(Integer)
    care_level = Column(String)
    special_requirements = Column(String)
    created_at = Column(Date, default=datetime.now)

class ShiftAssignmentModel(Base):
    """Shift assignment database model"""
    __tablename__ = 'shift_assignments'
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    service_user_id = Column(Integer, ForeignKey('service_users.id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    shift_time = Column(String)
    hours = Column(Integer)
    support_ratio = Column(Integer)
    location = Column(String)
    status = Column(String, default='scheduled')
    created_at = Column(Date, default=datetime.now)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///rota.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()