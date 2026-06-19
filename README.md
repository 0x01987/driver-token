# Driver Token MVP

Secure MVP for rewarding verified rideshare drivers with claimable ERC-20 tokens.

Max supply: 100,000,000 DRIVE.

## Architecture

Driver app -> login and wallet connect -> Uber OAuth -> backend verifies completed rides -> backend signs a claim proof -> driver claims tokens from the contract -> contract verifies proof and blocks duplicate ride claims.

## Stack

- Frontend: Next.js
- Backend: FastAPI, PostgreSQL, Redis-ready settings
- Smart contracts: Solidity, Hardhat, OpenZeppelin
- Auth: JWT plus OAuth provider tokens encrypted at rest

## Project Layout

- `backend/` FastAPI API, database models, claim signer, Uber OAuth boundary
- `contracts/` ERC-20 claim contract with access control, pausing, and signature verification
- `frontend/` Next.js app shell for signup, wallet connection, OAuth status, and claimable rides

## MVP Build Order

1. Configure `.env` files from each example file.
2. Start PostgreSQL and run backend migrations once added.
3. Deploy `DriverToken` with the backend oracle signer as `ORACLE_ROLE`.
4. Connect Uber OAuth using minimum approved scopes.
5. Sync completed rides off-chain.
6. Sign claim proofs server-side and submit them from the driver wallet.

## Security Notes

- Never ask drivers for Uber/Lyft passwords.
- Store only hashed external ride IDs for duplicate prevention.
- Encrypt OAuth refresh/access tokens before writing them to the database.
- Keep claim signing keys outside the web app runtime in production.
- Do not promise token price, yield, or investment returns.
