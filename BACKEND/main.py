from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, ConfigDict
from typing import Annotated
import models
from models import AlertType
from database import engine, SessionLocal
from sqlalchemy.orm import Session

#_Pydantic_Models_____________________________________________________________________________________________________________________________________________________________________________

class DeviceBase(BaseModel):
    hostname: str | None
    ip_address: str
    mac_address: str
    os_name: str | None
    os_version: str | None
    architecture: str | None
    manufacturer: str | None
    model: str | None
    serial_number: str | None
    form_factor: str | None
    hdd_capacity_gb: int | None
    hdd_available_gb: int | None
    is_managed: bool

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    model_config = ConfigDict(from_attributes=True)


class StatusBase(BaseModel):
    id: int
    device_id: int
    is_online: bool
    response_time_ms: int | None
    updated_at: datetime

class PingBase(BaseModel):
    id: int
    device_id: int
    is_online: bool
    response_time_ms: int | None
    updated_at: datetime

class AlertBase(BaseModel):
    id: int
    device_id: int
    alert_type: AlertType
    message: str
    acknowledged: bool
    sent_at: datetime
    resolved_at: datetime | None


#_FastAPI_Endpoints__________________________________________________________________________________________________________________________________________________________________________

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/devices/", response_model=DeviceResponse)
async def create_device(device: DeviceCreate, db: db_dependency):
    db_device = models.Device(**device.model_dump())
    db.add(db_device)
    db.commit()

    # Refreshing device instance with database generated fields (i.e. id, first_seen, last_seen) 
    db.refresh(db_device)
    return db_device


#_Backend_Logic_______________________________________________________________________________________________________________________________________________________________________________

