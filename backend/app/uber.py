from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass(frozen=True)
class UberTokenResponse:
    access_token: str
    refresh_token: str
    scopes: str


def uber_authorization_url(state: str) -> str:
    settings = get_settings()
    return (
        "https://login.uber.com/oauth/v2/authorize"
        f"?client_id={settings.uber_client_id}"
        f"&response_type=code"
        f"&redirect_uri={settings.uber_redirect_uri}"
        f"&scope={settings.uber_scopes}"
        f"&state={state}"
    )


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
