"""Vercel serverless entrypoint for the FastAPI application."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the src/ directory is importable when Vercel executes the function.
ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from app.main import app as fastapi_app  # noqa: E402

# Vercel expects a top-level `app` object that represents the ASGI application.
app = fastapi_app
