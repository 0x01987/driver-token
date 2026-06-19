from html import escape
from secrets import token_urlsafe

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.claims import sign_claim
from app.db import Base, engine, get_db
from app.models import Claim, ClaimStatus, DriverAccount, Ride, User, Wallet
from app.security import create_access_token, hash_password, verify_password
from app.uber import uber_authorization_url

app = FastAPI(title="Driver Token API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ClaimProofResponse(BaseModel):
    ride_id: str
    wallet: str
    ride_hash: str
    amount: int
    nonce: int
    signature: str


class WalletLinkRequest(BaseModel):
    user_id: str
    address: str = Field(pattern=r"^0x[a-fA-F0-9]{40}$")


class AuthRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


@app.on_event("startup")
def create_tables_for_mvp() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/auth/signup", response_model=AuthResponse)
def signup(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=422, detail="valid email is required")

    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="account already exists")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(access_token=create_access_token(user.id), user_id=user.id, email=user.email)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid email or password")

    return AuthResponse(access_token=create_access_token(user.id), user_id=user.id, email=user.email)


@app.get("/oauth/uber/start")
def start_uber_oauth(user_id: str = "demo") -> RedirectResponse:
    state = f"{user_id}:{token_urlsafe(24)}"
    return RedirectResponse(uber_authorization_url(state), status_code=302)


@app.get("/oauth/uber/callback")
def uber_callback(code: str | None = None, state: str | None = None, error: str | None = None) -> HTMLResponse:
    if error:
        return HTMLResponse(f"<h1>Uber connection failed</h1><p>{escape(error)}</p>", status_code=400)
    if not code:
        return HTMLResponse("<h1>Uber connection failed</h1><p>Missing OAuth code.</p>", status_code=400)
    return HTMLResponse(
        "<h1>Uber connected</h1><p>You can close this tab and return to Driver Token.</p>",
        status_code=200,
    )


@app.post("/wallets")
def link_wallet(payload: WalletLinkRequest, db: Session = Depends(get_db)) -> dict:
    existing = db.scalar(select(Wallet).where(Wallet.address == payload.address.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="wallet already linked")

    wallet = Wallet(user_id=payload.user_id, address=payload.address.lower(), is_primary=True)
    db.add(wallet)
    db.commit()
    return {"id": wallet.id, "address": wallet.address}


@app.get("/rides/claimable")
def claimable_rides(user_id: str, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(Ride)
        .join(DriverAccount, DriverAccount.id == Ride.driver_account_id)
        .where(DriverAccount.user_id == user_id)
        .where(Ride.claim_status == ClaimStatus.unclaimed.value)
        .order_by(Ride.completed_at.desc())
    ).all()
    return [
        {
            "id": ride.id,
            "platform": ride.platform,
            "completed_at": ride.completed_at.isoformat(),
            "distance_meters": ride.distance_meters,
            "duration_seconds": ride.duration_seconds,
            "token_amount": ride.token_amount,
        }
        for ride in rows
    ]


@app.post("/rides/{ride_id}/claim-proof", response_model=ClaimProofResponse)
def create_claim_proof(
    ride_id: str,
    user_id: str,
    wallet: str,
    db: Session = Depends(get_db),
) -> ClaimProofResponse:
    linked_wallet = db.scalar(
        select(Wallet).where(Wallet.user_id == user_id).where(Wallet.address == wallet.lower())
    )
    if not linked_wallet:
        raise HTTPException(status_code=403, detail="wallet is not linked to this user")

    ride = db.scalar(
        select(Ride)
        .join(DriverAccount, DriverAccount.id == Ride.driver_account_id)
        .where(Ride.id == ride_id)
        .where(DriverAccount.user_id == user_id)
    )
    if not ride or ride.claim_status != ClaimStatus.unclaimed.value:
        raise HTTPException(status_code=404, detail="claimable ride not found")

    signature = sign_claim(wallet, ride.external_ride_hash, ride.token_amount, ride.nonce)
    claim = Claim(ride_id=ride.id, wallet_address=wallet.lower(), signature=signature)
    ride.claim_status = ClaimStatus.signed.value
    db.add(claim)
    db.commit()

    return ClaimProofResponse(
        ride_id=ride.id,
        wallet=wallet,
        ride_hash=ride.external_ride_hash,
        amount=ride.token_amount,
        nonce=ride.nonce,
        signature=signature,
    )
