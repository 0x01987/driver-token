# Backend

FastAPI service for user auth, wallet linking, Uber OAuth, ride verification, and signed token claim proofs.

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Copy `.env.example` to `.env` and fill in secrets before running.
