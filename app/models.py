from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
metadata = Base.metadata
class VehicleLog(Base):
    __tablename__ = 'vehicle_logs'

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, index=True, nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    charged_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)  # True if vehicle is still parked


class VehicleRegistration(Base):
    __tablename__ = 'vehicle_registration'

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, nullable=False)
