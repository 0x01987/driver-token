# Deployment

This project deploys in three parts:

1. `frontend/` to Vercel.
2. `backend/` to Render, Railway, Fly.io, or another container/Python host.
3. `contracts/` to Base Sepolia, Polygon Amoy, or mainnet after audit readiness.

## Required Secrets

Backend:

- `DATABASE_URL`
- `JWT_SECRET`
- `TOKEN_ENCRYPTION_KEY`
- `CLAIM_SIGNER_PRIVATE_KEY`
- `CHAIN_ID`
- `DRIVER_TOKEN_CONTRACT`
- `UBER_CLIENT_ID`
- `UBER_CLIENT_SECRET`
- `UBER_REDIRECT_URI`
- `UBER_SCOPES`

Frontend:

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_CHAIN_ID`
- `NEXT_PUBLIC_DRIVER_TOKEN_CONTRACT`

Contracts:

- `BASE_SEPOLIA_RPC_URL` or `POLYGON_AMOY_RPC_URL`
- `DEPLOYER_PRIVATE_KEY`
- `ADMIN_ADDRESS`
- `ORACLE_ADDRESS`
- `PAUSER_ADDRESS`

## GitHub

```powershell
git init
git add .
git commit -m "Initial secure driver token MVP"
git branch -M main
git remote add origin https://github.com/<owner>/<repo>.git
git push -u origin main
```

## Frontend on Vercel

Use `frontend/` as the project root. Set:

```text
NEXT_PUBLIC_API_URL=https://<backend-host>
NEXT_PUBLIC_CHAIN_ID=84532
NEXT_PUBLIC_DRIVER_TOKEN_CONTRACT=0x...
```

## Backend on Render

Use `render.yaml` from the repo root or create a Python web service with:

```text
Root directory: backend
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Contract Deploy

```powershell
cd contracts
npm install
npx hardhat test
npx hardhat run scripts/deploy.ts --network baseSepolia
```

After deployment, set `DRIVER_TOKEN_CONTRACT` in the backend and `NEXT_PUBLIC_DRIVER_TOKEN_CONTRACT` in the frontend.
