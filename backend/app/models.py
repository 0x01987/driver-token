from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def new_id() -> str:
    return str(uuid4())


class Platform(str, Enum):
    uber = "uber"
    lyft = "lyft"


class ClaimStatus(str, Enum):
    unclaimed = "unclaimed"
    signed = "signed"
    claimed = "claimed"
    blocked = "blocked"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    wallets: Mapped[list["Wallet"]] = relationship(back_populates="user")
    driver_accounts: Mapped[list["DriverAccount"]] = relationship(back_populates="user")


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    address: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="wallets")


class DriverAccount(Base):
    __tablename__ = "driver_accounts"
    __table_args__ = (UniqueConstraint("platform", "external_driver_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    platform: Mapped[Platform] = mapped_column(String)
    external_driver_id: Mapped[str] = mapped_column(String)
    encrypted_access_token: Mapped[str] = mapped_column(String)
    encrypted_refresh_token: Mapped[str] = mapped_column(String)
    scopes: Mapped[str] = mapped_column(String)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="driver_accounts")


class Ride(Base):
    __tablename__ = "rides"
    __table_args__ = (UniqueConstraint("platform", "external_ride_hash"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    driver_account_id: Mapped[str] = mapped_column(ForeignKey("driver_accounts.id"), index=True)
    platform: Mapped[Platform] = mapped_column(String)
    external_ride_hash: Mapped[str] = mapped_column(String, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime)
    distance_meters: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    fare_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    claim_status: Mapped[ClaimStatus] = mapped_column(String, default=ClaimStatus.unclaimed.value)
    token_amount: Mapped[int] = mapped_column(Integer, default=10)
    nonce: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Claim(Base):
    __tablename__ = "claims"
    __table_args__ = (UniqueConstraint("ride_id"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    ride_id: Mapped[str] = mapped_column(ForeignKey("rides.id"), index=True)
    wallet_address: Mapped[str] = mapped_column(String, index=True)
    signature: Mapped[str] = mapped_column(String)
    tx_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    ip_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[str] = mapped_column(String, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
