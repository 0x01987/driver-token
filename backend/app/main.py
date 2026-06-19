from html import escape
from secrets import token_urlsafe

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.claims import sign_claim
from app.db import Base, engine, get_db
from app.models import Claim, ClaimStatus, DriverAccount, Ride, Wallet
from app.uber import uber_authorization_url

app = FastAPI(title="Driver Token API")


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


@app.on_event("startup")
def create_tables_for_mvp() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


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
