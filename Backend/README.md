# VMC Bridge - Backend

Minimal FastAPI backend for VMC Bridge.

Quickstart

1. Install Python 3.11 or 3.12 and create & activate a virtual environment
   - Windows (choose a specific version): `py -3.11 -m venv .venv` then `./.venv/Scripts/Activate.ps1` (PowerShell)
   - macOS/Linux: `python3.11 -m venv .venv` then `source .venv/bin/activate`
2. Upgrade pip and build tools (recommended):
   - `python -m pip install --upgrade pip setuptools wheel build`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` → `.env` and edit if necessary
5. Start server: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Endpoints
- GET /health -> { "status": "ok" }

Troubleshooting

- If pip tries to build `pydantic-core` from source and fails (e.g., on Python 3.13), switch to Python 3.11 or 3.12 where prebuilt wheels are available, or install the Rust toolchain (https://rustup.rs) and ensure `cargo` is on PATH before running `pip install`.
- If installation still fails, make sure you ran the upgrade in step 2 (`pip`, `setuptools`, `wheel`, `build`) and share the error output here so I can help.
