from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from app.config import get_settings


@dataclass(frozen=True)
class UberTokenResponse:
    access_token: str
    refresh_token: str
    scopes: str


def uber_authorization_url(state: str) -> str:
    settings = get_settings()
    query = urlencode(
        {
            "client_id": settings.uber_client_id,
            "response_type": "code",
            "redirect_uri": settings.uber_redirect_uri,
            "scope": settings.uber_scopes,
            "state": state,
        }
    )
    return f"https://login.uber.com/oauth/v2/authorize?{query}"


async def exchange_uber_code(code: str) -> UberTokenResponse:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://login.uber.com/oauth/v2/token",
            data={
                "client_id": settings.uber_client_id,
                "client_secret": settings.uber_client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": settings.uber_redirect_uri,
                "code": code,
            },
        )
        response.raise_for_status()
        payload = response.json()
    return UberTokenResponse(
        access_token=payload["access_token"],
        refresh_token=payload["refresh_token"],
        scopes=payload.get("scope", settings.uber_scopes),
    )


async def fetch_uber_profile(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.uber.com/v1/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
