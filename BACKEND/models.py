from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import ForeignKey,String, Integer, Enum, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base


class Device(Base):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    hostname: Mapped[str | None] = mapped_column(String(45))
    ip_address: Mapped[str] = mapped_column(String(45)) # Thinking about setting this as unique for the sake of updating records as opposed to making new ones. Difficult tho since IPs change.
    mac_address: Mapped[str] = mapped_column(String(17), unique=True)
    os_name: Mapped[str | None] = mapped_column(String(100))
    os_version: Mapped[str | None] = mapped_column(String(100))
    architecture: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    serial_number: Mapped[str | None] = mapped_column(String(100))
    form_factor: Mapped[str | None] = mapped_column(String(50))
    hdd_capacity_gb: Mapped[int | None] = mapped_column(Integer)
    hdd_available_gb: Mapped[int | None] = mapped_column(Integer)
    is_managed: Mapped[bool] = mapped_column(default=False)
    first_seen: Mapped[datetime] = mapped_column(server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime, server_default=func.now()) # This will look exactly like first_seen. This needs to have logic inside ping scanning so the field can be updated.

    status: Mapped["DeviceStatus"] = relationship(back_populates="device", uselist=False)
    pings: Mapped[list["PingHistory"]] = relationship(back_populates="device", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="device", cascade="all, delete-orphan")


class DeviceStatus(Base):
    __tablename__ = 'device_status'

    id: Mapped[int]  = mapped_column(primary_key=True, autoincrement=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), unique=True)
    is_online: Mapped[bool] = mapped_column(server_default=False)   
    response_time_ms: Mapped[int | None] = mapped_column()
    updated_at: Mapped[datetime] =  mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    device: Mapped["Device"] = relationship(back_populates="status")


class PingHistory(Base):
    __tablename__ = 'ping_history'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    is_online: Mapped[bool] = mapped_column(default=False)   
    response_time_ms: Mapped[int | None] = mapped_column()
    updated_at: Mapped[datetime] =  mapped_column(DateTime, server_default=func.now())

    device: Mapped["Device"] = relationship(back_populates="pings")


class AlertType(PyEnum):
    DEVICE_DOWN = "device_down"
    DEVICE_UP = "device_up"
    OUTDATED_OS = "outdated_os"
    HIGH_CPU = "high_cpu"
    HIGH_RAM = "high_ram"


class Alert(Base):
    __tablename__ = 'alerts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType))
    message: Mapped[str] = mapped_column(Text)
    acknowledged: Mapped[bool] = mapped_column(default=False)  
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime) # Need to build logic to set this as resolved only when alerts are actually resolved.

    device: Mapped["Device"] = relationship(back_populates="alerts")



#_STRETCH_TABLES_____________________________________________________________________________________________________________________________________________________________________________________________
class RoleType(Base):
    ADMINISTRATOR = "admin"
    VIEWER = "viewer"


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    role_name: Mapped[RoleType] = mapped_column(Enum(RoleType))

    user: Mapped["User"] = relationship(back_populates="users", uselist=False)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    role: Mapped["Role"] = relationship(back_populates="roles")




class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    tag_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # color_hex: Mapped[str] = mapped_column(String(7)) # Not sure how to implement this yet or even if I want to use this

    device_tag: Mapped[list["DeviceTag"]] = relationship(back_populates="device_tags")


# Junction Table
class DeviceTag(Base):
    __tablename__ = 'device_tags'

    device_id: Mapped[int] = mapped_column(primary_key=True,index=True)
    tag_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    tag: Mapped[list["Tag"]] = relationship(back_populates="tags", cascade="all, delete-orphan")
    device: Mapped[list["Device"]] = relationship(back_populates="tags", cascade="all, delete-orphan")




class Processes(Base):
    __table_name = 'running_processes'


class Applications(Base):
    __table_name__ = 'installed_applications'